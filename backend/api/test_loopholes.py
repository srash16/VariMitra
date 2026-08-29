#!/usr/bin/env python3
"""Test script to identify loopholes in VariMitra API."""

from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_open_endpoints():
    print("Testing open endpoints...")
    # Health endpoint
    resp = client.get("/health")
    assert resp.status_code == 200
    print("  /health accessible")

    # Catalog endpoint
    resp = client.get("/sync/catalog")
    assert resp.status_code == 200
    print("  /sync/catalog accessible")

    # Family pairing start
    resp = client.post("/family/pair/start", json={"family_device_id": "test-device"})
    assert resp.status_code == 200
    data = resp.json()
    print(f"  /family/pair/start accessible, got link_id: {data['family_link_id']}")
    return data["family_link_id"], data["pairing_code"], data["qr_token"]

def test_pairing_code_bruteforce_simulation(link_id, valid_code):
    print("\nSimulating pairing code brute-force (limited attempts)...")
    # Try a few invalid codes
    for i in range(5):
        fake_code = "AAAAAA"  # simple
        resp = client.post("/family/pair/complete", json={"pilgrim_device_id": "pilgrim-1", "pairing_code": fake_code})
        if resp.status_code == 404:
            print(f"    Attempt {i+1}: invalid code -> 404 (as expected)")
        else:
            print(f"    Attempt {i+1}: unexpected response {resp.status_code}")
    # Try the valid code (should succeed)
    resp = client.post("/family/pair/complete", json={"pilgrim_device_id": "pilgrim-1", "pairing_code": valid_code})
    if resp.status_code == 200:
        print(f"    Valid code -> 200 OK (pairing successful)")
    else:
        print(f"    Valid code -> unexpected {resp.status_code}")

def test_queue_spam():
    print("\nTesting queue endpoint for potential spam...")
    # Insert a lost person report
    item_id = str(uuid4())
    payload = {
        "device_id": "spam-device",
        "items": [
            {
                "id": item_id,
                "entity_type": "lost_person_report",
                "payload": {
                    "description": "Spam test",
                    "location": "Nowhere"
                }
            }
        ]
    }
    resp = client.post("/sync/queue", json=payload)
    assert resp.status_code == 200
    print(f"  Successfully inserted spam report, item_id: {item_id}")
    # Try to insert duplicate (should return duplicate)
    resp2 = client.post("/sync/queue", json=payload)
    assert resp2.status_code == 200
    assert resp2.json()["accepted"][0]["status"] == "duplicate"
    print("  Duplicate detection works")

def test_family_status_without_auth():
    print("\nTesting family status endpoint access...")
    # First create a link
    link_id, _, _ = test_open_endpoints()  # but we need to avoid duplicate prints; let's refactor
    # Instead, we'll create a link directly
    resp = client.post("/family/pair/start", json={"family_device_id": "status-test"})
    assert resp.status_code == 200
    data = resp.json()
    link_id = data["family_link_id"]
    # Query status by family_link_id
    resp = client.get(f"/family/status?family_link_id={link_id}")
    assert resp.status_code == 200
    print(f"  Status accessible by family_link_id: {resp.json()['is_active']}")
    # Query status by device_id (family_device_id)
    resp = client.get(f"/family/status?device_id=status-test")
    assert resp.status_code == 200
    print(f"  Status accessible by device_id: {resp.json()['is_active']}")

def test_error_exposure():
    print("\nTesting error message exposure...")
    # Try to insert a lost_person_report with invalid family_link_id (non-existent UUID)
    # This should cause foreign key violation in Postgres, but in MemoryRepository it will accept.
    # We'll see what happens.
    item_id = str(uuid4())
    payload = {
        "device_id": "error-test",
        "items": [
            {
                "id": item_id,
                "entity_type": "lost_person_report",
                "payload": {
                    "description": "Test",
                    "location": "Here",
                    "family_link_id": "00000000-0000-0000-0000-000000000000"  # unlikely to exist
                }
            }
        ]
    }
    resp = client.post("/sync/queue", json=payload)
    print(f"  Response status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"  Error response: {resp.json()}")
    else:
        print(f"  Insert succeeded (maybe MemoryRepository allows null FK)")

if __name__ == "__main__":
    print("=== Loophole Testing ===")
    link_id, valid_code, qr_token = test_open_endpoints()
    test_pairing_code_bruteforce_simulation(link_id, valid_code)
    test_queue_spam()
    test_family_status_without_auth()
    test_error_exposure()
    print("\n=== Testing complete ===")