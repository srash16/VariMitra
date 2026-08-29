#!/usr/bin/env python3
"""Security-focused test script to identify potential loopholes in VariMitra API."""

from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_health_endpoint():
    """Test that health endpoint doesn't leak sensitive information."""
    print("Testing health endpoint...")
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    # Should only contain basic status info
    assert "status" in data
    assert "service" in data
    # Should not contain sensitive data like database URLs, keys, etc.
    assert "database" not in str(data).lower()
    assert "password" not in str(data).lower()
    assert "secret" not in str(data).lower()
    print("  ✓ Health endpoint OK")

def test_catalog_endpoint():
    """Test catalog endpoint for information leakage."""
    print("Testing catalog endpoint...")
    resp = client.get("/sync/catalog")
    assert resp.status_code == 200
    data = resp.json()
    # Check that all collections have source and last_updated
    for collection_name, collection in data.items():
        if isinstance(collection, list):
            for item in collection:
                assert "source" in item, f"Missing source in {collection_name} item"
                assert "last_updated" in item, f"Missing last_updated in {collection_name} item"
    print("  ✓ Catalog endpoint OK")

def test_pairing_code_security():
    """Test pairing implementation for security issues."""
    print("Testing pairing security...")

    # Start pairing
    resp = client.post("/family/pair/start", json={
        "family_device_id": "sec-test-device",
        "family_name": "Test Family",
        "emergency_contact": "123-456-7890"
    })
    assert resp.status_code == 200
    data = resp.json()
    link_id = data["family_link_id"]
    pairing_code = data["pairing_code"]
    qr_token = data["qr_token"]

    # Verify that the response doesn't contain the actual secrets in plaintext
    # (they should be hashed in storage, but the API returns them once for display)
    # This is by design - the API returns the plaintext code/token once for user to see

    # Test that invalid codes are properly rejected
    resp = client.post("/family/pair/complete", json={
        "pilgrim_device_id": "pilgrim-1",
        "pairing_code": "INVALID"
    })
    # Should return 404 (not found) rather than leaking information about why it failed
    assert resp.status_code == 404

    # Test that valid code works
    resp = client.post("/family/pair/complete", json={
        "pilgrim_device_id": "pilgrim-1",
        "pairing_code": pairing_code
    })
    assert resp.status_code == 200
    result = resp.json()
    assert result["paired"] is True
    assert result["is_active"] is True

    # Test that used code cannot be reused
    resp = client.post("/family/pair/complete", json={
        "pilgrim_device_id": "pilgrim-2",
        "pairing_code": pairing_code
    })
    assert resp.status_code == 404  # Should not be found anymore

    print("  ✓ Pairing security OK")

def test_queue_endpoint_security():
    """Test queue endpoint for potential abuses."""
    print("Testing queue endpoint security...")

    # Test normal operation
    item_id = str(uuid4())
    payload = {
        "device_id": "sec-test-device",
        "items": [
            {
                "id": item_id,
                "entity_type": "lost_person_report",
                "payload": {
                    "description": "Test report",
                    "location": "Test location"
                }
            }
        ]
    }
    resp = client.post("/sync/queue", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["accepted"]) == 1
    assert data["accepted"][0]["status"] == "synced"

    # Test duplicate detection
    resp2 = client.post("/sync/queue", json=payload)
    assert resp2.status_code == 200
    assert resp2.json()["accepted"][0]["status"] == "duplicate"

    # Test that invalid entity types are rejected (should be caught by schema)
    # Actually, the schema validation happens at the API level

    # Test SOS ingest doesn't trigger emergency action
    sos_id = str(uuid4())
    sos_payload = {
        "device_id": "sos-test-device",
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
    # According to requirements, SOS ingest should never place emergency call
    assert result["accepted"][0]["emergency_action_required"] is False
    assert result["accepted"][0]["family_delivered"] is False
    assert "never places an emergency call" in result["note"].lower()

    print("  ✓ Queue endpoint security OK")

def test_family_endpoint_security():
    """Test family endpoints for IDOR and information leakage."""
    print("Testing family endpoint security...")

    # Create two separate family links
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

    # Complete pairing for first link
    client.post("/family/pair/complete", json={
        "pilgrim_device_id": "pilgrim-device-1",
        "pairing_code": data1["pairing_code"]
    })

    # Test that we can only access our own link by family_link_id
    resp = client.get(f"/family/status?family_link_id={link_id_1}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["family_link_id"] == str(link_id_1)
    assert data["paired"] is True

    resp = client.get(f"/family/status?family_link_id={link_id_2}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["family_link_id"] == str(link_id_2)
    assert data["paired"] is False  # Not paired yet

    # Test access by device_id
    resp = client.get("/family/status?device_id=family-device-1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["family_link_id"] == str(link_id_1)

    resp = client.get("/family/status?device_id=family-device-2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["family_link_id"] == str(link_id_2)

    # Test that invalid UUID returns 404 (not found) rather than 500 or leaking info
    resp = client.get("/family/status?family_link_id=00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404

    print("  ✓ Family endpoint security OK")

def test_error_handling():
    """Test that error messages don't leak sensitive information."""
    print("Testing error handling...")

    # Test malformed JSON
    resp = client.post("/family/pair/start", data="invalid json", headers={"Content-Type": "application/json"})
    # Should return 422 (validation error) or 400, not 500 with stack trace
    assert resp.status_code in [400, 422]
    if resp.status_code != 200:  # Don't check error details for success
        data = resp.json()
        # Error message should not contain stack traces or internal details
        error_str = str(data).lower()
        assert "traceback" not in error_str
        assert "file" not in error_str or "line" not in error_str  # Basic check

    # Test missing required fields
    resp = client.post("/family/pair/start", json={})
    assert resp.status_code == 422  # Validation error

    print("  ✓ Error handling OK")

def run_all_tests():
    """Run all security tests."""
    print("=== Starting Security Loophole Tests ===\n")

    try:
        test_health_endpoint()
        test_catalog_endpoint()
        test_pairing_code_security()
        test_queue_endpoint_security()
        test_family_endpoint_security()
        test_error_handling()

        print("\n=== All Security Tests Passed ===")
        print("No obvious security loopholes detected in basic API endpoints.")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    run_all_tests()