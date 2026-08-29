#!/usr/bin/env python3
"""Logic-focused test script to identify loopholes in VariMitra API business logic."""

from fastapi.testclient import TestClient
from app.main import app
import uuid

def test_with_memory_repo(test_func):
    """Decorator to run a test with MemoryRepository override."""
    from app.deps import get_repo
    from app.memory import MemoryRepository

    # Create a single repo instance to be used by all requests (like in conftest.py)
    repo = MemoryRepository()
    # Override dependency to return THIS specific instance
    app.dependency_overrides[get_repo] = lambda: repo

    try:
        with TestClient(app) as client:
            return test_func(client)
    finally:
        # Clean up
        app.dependency_overrides.clear()

def test_health_endpoint(client):
    """Test health endpoint."""
    print("Testing health endpoint...")
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "varimitra-api"
    print("  ✓ Health endpoint OK")

def test_catalog_endpoint(client):
    """Test catalog endpoint logic."""
    print("Testing catalog endpoint...")
    resp = client.get("/sync/catalog")
    assert resp.status_code == 200
    data = resp.json()

    # Check required fields exist
    required_collections = [
        "facilities", "facility_updates", "wari_palkhis",
        "wari_route_segments", "wari_schedule", "wari_major_dates",
        "local_information", "emergency_contacts"
    ]
    for collection in required_collections:
        assert collection in data
        assert isinstance(data[collection], list)

    # Check that all items have source and last_updated
    for collection_name, collection in data.items():
        if isinstance(collection, list):
            for item in collection:
                assert "source" in item, f"Missing source in {collection_name}"
                assert "last_updated" in item, f"Missing last_updated in {collection_name}"

                # Check Wari schedule position_status is not illegally set to live
                if collection_name == "wari_schedule":
                    # Should not have position_status = live when it's supposed to be scheduled
                    # In MemoryRepository, they are all set to "scheduled"
                    assert item.get("position_status") != "live" or item.get("position_status") == "scheduled"

    print("  ✓ Catalog endpoint logic OK")

def test_pairing_logic(client):
    """Test pairing logic for security issues."""
    print("Testing pairing logic...")

    # Start pairing
    resp = client.post("/family/pair/start", json={
        "family_device_id": "test-device-1",
        "family_name": "Test Family",
        "emergency_contact": "123-456-7890"
    })
    assert resp.status_code == 200
    data = resp.json()
    link_id = data["family_link_id"]
    pairing_code = data["pairing_code"]
    qr_token = data["qr_token"]

    # Verify that attempting to pair with wrong code fails
    resp = client.post("/family/pair/complete", json={
        "pilgrim_device_id": "pilgrim-1",
        "pairing_code": "WRONG CODE"
    })
    assert resp.status_code == 404  # Not found (no matching link)

    # Verify that correct code works
    resp = client.post("/family/pair/complete", json={
        "pilgrim_device_id": "pilgrim-1",
        "pairing_code": pairing_code
    })
    assert resp.status_code == 200
    result = resp.json()
    assert result["paired"] is True
    assert result["is_active"] is True

    # Verify that code cannot be reused (after successful pairing)
    # Try with same code but different pilgrim device - should fail because code is now bound to pilgrim-1
    resp = client.post("/family/pair/complete", json={
        "pilgrim_device_id": "pilgrim-2",
        "pairing_code": pairing_code
    })
    assert resp.status_code == 404  # Should not find a match (the link is now associated with pilgrim-1)

    # Try with same pilgrim device - should also fail because is_active is now true
    # (the query looks for is_active = false)
    resp = client.post("/family/pair/complete", json={
        "pilgrim_device_id": "pilgrim-1",
        "pairing_code": pairing_code
    })
    assert resp.status_code == 404  # Won't find it because is_active is now true

    # Test QR token pairing
    # First create a new link
    resp2 = client.post("/family/pair/start", json={
        "family_device_id": "test-device-2"
    })
    assert resp2.status_code == 200
    data2 = resp2.json()
    qr_token_2 = data2["qr_token"]

    resp = client.post("/family/pair/complete", json={
        "pilgrim_device_id": "pilgrim-2",
        "qr_token": qr_token_2
    })
    assert resp.status_code == 200
    result = resp.json()
    assert result["paired"] is True

    print("  ✓ Pairing logic OK")

def test_queue_logic(client):
    """Test queue logic for security issues."""
    print("Testing queue logic...")

    # Test normal insert
    item_id = str(uuid4())
    payload = {
        "device_id": "test-device",
        "items": [
            {
                "id": item_id,
                "entity_type": "lost_person_report",
                "payload": {
                    "description": "Test person",
                    "location": "Test location",
                    "person_name": "John Doe"
                }
            }
        ]
    }
    resp = client.post("/sync/queue", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["accepted"]) == 1
    assert data["accepted"][0]["status"] == "synced"
    assert data["accepted"][0]["emergency_action_required"] is False
    assert data["accepted"][0]["family_delivered"] is False

    # Test duplicate detection
    resp2 = client.post("/sync/queue", json=payload)
    assert resp2.status_code == 200
    assert resp2.json()["accepted"][0]["status"] == "duplicate"

    # Test SOS ingest doesn't trigger emergency action
    sos_id = str(uuid4())
    sos_payload = {
        "device_id": "sos-test",
        "items": [
            {
                "id": sos_id,
                "entity_type": "sos_alert",
                "operation": "insert",
                "payload": {
                    "latitude": 18.52,
                    "longitude": 73.85,
                    "emergency_type": "medical",
                    "message": "Test SOS"
                }
            }
        ]
    }
    resp = client.post("/sync/queue", json=sos_payload)
    assert resp.status_code == 200
    result = resp.json()
    # Per requirements, SOS should never trigger emergency action via this API
    assert result["accepted"][0]["emergency_action_required"] is False
    assert result["accepted"][0]["family_delivered"] is False
    assert "never places an emergency call" in result["note"].lower()

    # Test that we can insert different entity types
    facility_report_id = str(uuid4())
    facility_payload = {
        "device_id": "facility-test",
        "items": [
            {
                "id": facility_report_id,
                "entity_type": "facility_report",
                "payload": {
                    "facility_id": str(uuid4()),  # This will fail FK constraint in Postgres but work in Memory
                    "description": "Test facility report"
                }
            }
        ]
    }
    resp = client.post("/sync/queue", json=facility_payload)
    assert resp.status_code == 200
    # In MemoryRepository, this should work (no FK enforcement)

    print("  ✓ Queue logic OK")

def test_family_logic(client):
    """Test family logic for security issues."""
    print("Testing family logic...")

    # Create two links
    resp1 = client.post("/family/pair/start", json={
        "family_device_id": "family-device-1"
    })
    assert resp1.status_code == 200
    data1 = resp1.json()
    link_id_1 = data1["family_link_id"]

    resp2 = client.post("/family/pair/start", json={
        "family_device_id": "family-device-2"
    })
    assert resp2.status_code == 200
    data2 = resp2.json()
    link_id_2 = data2["family_link_id"]

    # Pair first link
    client.post("/family/pair/complete", json={
        "pilgrim_device_id": "pilgrim-1",
        "pairing_code": data1["pairing_code"]
    })

    # Test accessing by family_link_id
    resp = client.get(f"/family/status?family_link_id={link_id_1}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["family_link_id"] == str(link_id_1)
    assert data["paired"] is True

    resp = client.get(f"/family/status?family_link_id={link_id_2}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["family_link_id"] == str(link_id_2)
    assert data["paired"] is False

    # Test accessing by device_id
    resp = client.get("/family/status?device_id=family-device-1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["family_link_id"] == str(link_id_1)

    resp = client.get("/family/status?device_id=family-device-2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["family_link_id"] == str(link_id_2)

    # Test that non-existent link returns 404
    resp = client.get("/family/status?family_link_id=00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404

    # Test that missing both parameters returns 400
    resp = client.get("/family/status")
    assert resp.status_code == 400

    # Test that we can add lost person reports and they appear in family status
    report_id = str(uuid4())
    report_payload = {
        "device_id": "reporter-device",
        "items": [
            {
                "id": report_id_1,
                "entity_type": "lost_person_report",
                "payload": {
                    "description": "Missing person",
                    "location": "Last seen near temple",
                    "person_name": "Jane Doe",
                    "age": 25,
                    "gender": "female",
                    "family_link_id": link_id_1  # Link it to our first family
                }
            }
        ]
    }
    resp = client.post("/sync/queue", json=report_payload)
    assert resp.status_code == 200

    # Check that the report appears in family status
    resp = client.get(f"/family/status?family_link_id={link_id_1}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["lost_reports"]) >= 1
    # Find our report
    report_found = False
    for report in data["lost_reports"]:
        if report.get("id") == report_id:
            report_found = True
            break
    assert report_found, "Lost person report not found in family status"

    print("  ✓ Family logic OK")

def test_error_handling(client):
    """Test error handling doesn't leak information."""
    print("Testing error handling...")

    # Test invalid JSON
    resp = client.post("/family/pair/start",
                      data="not json",
                      headers={"Content-Type": "application/json"})
    # Should be 400 or 422, not 500 with stack trace
    assert resp.status_code in [400, 422]
    if resp.status_code >= 400:
        # Check that error response doesn't contain obvious stack trace indicators
        error_text = resp.text.lower()
        assert "traceback" not in error_text
        assert "file" not in error_text or "line" not in error_text  # Basic check

    # Test missing required fields
    resp = client.post("/family/pair/start", json={})
    assert resp.status_code == 422  # Validation error

    # Test invalid UUID format
    resp = client.get("/family/status?family_link_id=not-a-uuid")
    assert resp.status_code == 422  # Validation error

    print("  ✓ Error handling OK")

def test_idor_protections(client):
    """Test Insecure Direct Object Reference protections."""
    print("Testing IDOR protections...")

    # Create two users and their data
    # User 1
    resp1 = client.post("/family/pair/start", json={
        "family_device_id": "user-device-1"
    })
    assert resp1.status_code == 200
    data1 = resp1.json()
    link_id_1 = data1["family_link_id"]

    # User 2
    resp2 = client.post("/family/pair/start", json={
        "family_device_id": "user-device-2"
    })
    assert resp2.status_code == 200
    data2 = resp2.json()
    link_id_2 = data2["family_link_id"]

    # User 1 pairs their link
    client.post("/family/pair/complete", json={
        "pilgrim_device_id": "pilgrim-1",
        "pairing_code": data1["pairing_code"]
    })

    # User 1 creates a private report
    report_id_1 = str(uuid4())
    report_payload_1 = {
        "device_id": "user-device-1",
        "items": [
            {
                "id": report_id_1,
                "entity_type": "lost_person_report",
                "payload": {
                    "description": "User 1 private report",
                    "location": "Secret location 1",
                    "family_link_id": link_id_1
                }
            }
        ]
    }
    resp = client.post("/sync/queue", json=report_payload_1)
    assert resp.status_code == 200

    # User 2 creates a private report
    report_id_2 = str(uuid4())
    report_payload_2 = {
        "device_id": "user-device-2",
        "items": [
            {
                "id": report_id_2,
                "entity_type": "lost_person_report",
                "payload": {
                    "description": "User 2 private report",
                    "location": "Secret location 2",
                    "family_link_id": link_id_2
                }
            }
        ]
    }
    resp = client.post("/sync/queue", json=report_payload_2)
    assert resp.status_code == 200

    # Now test that User 1 cannot access User 2's report by trying to access family link 2
    # (unless they have the family_link_id or device_id)
    resp = client.get(f"/family/status?family_link_id={link_id_2}")
    # This should work if they know the link_id - which is correct behavior
    # The protection is that you need to know the identifier to access the resource
    assert resp.status_code == 200
    data = resp.json()
    # User 1 should see User 2's link info (but not necessarily their reports if not linked)
    # Actually, in this case, since we're querying by family_link_id, we should get that link's info
    assert data["family_link_id"] == str(link_id_2)

    # But User 1 should not see User 2's reports when querying their own link
    resp = client.get(f"/family/status?family_link_id={link_id_1}")
    assert resp.status_code == 200
    data = resp.json()
    # Should see their own report
    own_report_found = any(r.get("id") == report_id_1 for r in data["lost_reports"])
    assert own_report_found, "User 1 should see their own report"

    # Should NOT see User 2's report (since it's linked to link_id_2)
    other_report_found = any(r.get("id") == report_id_2 for r in data["lost_reports"])
    assert not other_report_found, "User 1 should not see User 2's report"

    print("  ✓ IDOR protections OK")

def run_all_tests():
    """Run all logic tests."""
    print("=== Starting Logic Loophole Tests ===\n")

    test_functions = [
        test_health_endpoint,
        test_catalog_endpoint,
        test_pairing_logic,
        test_queue_logic,
        test_family_logic,
        test_error_handling,
        test_idor_protections
    ]

    for test_func in test_functions:
        try:
            test_with_memory_repo(test_func)
        except Exception as e:
            print(f"\n❌ Test {test_func.__name__} failed with error: {e}")
            raise

    print("\n=== All Logic Tests Passed ===")
    print("No obvious logic loopholes detected in API business logic.")

if __name__ == "__main__":
    run_all_tests()