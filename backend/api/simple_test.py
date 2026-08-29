#!/usr/bin/env python3
"""Simple test script to check basic functionality."""

from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_basic():
    print("Testing basic endpoints...")
    # Health endpoint
    resp = client.get("/health")
    print(f"Health: {resp.status_code}")
    assert resp.status_code == 200

    # Catalog endpoint
    resp = client.get("/sync/catalog")
    print(f"Catalog: {resp.status_code}")
    assert resp.status_code == 200

    # Family pairing start
    resp = client.post("/family/pair/start", json={"family_device_id": "test-device"})
    print(f"Pair start: {resp.status_code}")
    assert resp.status_code == 200
    data = resp.json()
    link_id = data["family_link_id"]
    pairing_code = data["pairing_code"]
    qr_token = data["qr_token"]
    print(f"  Got link_id: {link_id}")

    # Try invalid pairing code
    resp = client.post("/family/pair/complete", json={"pilgrim_device_id": "pilgrim-1", "pairing_code": "WRONG"})
    print(f"Invalid code: {resp.status_code}")
    # Should be 404

    # Try valid pairing code
    resp = client.post("/family/pair/complete", json={"pilgrim_device_id": "pilgrim-1", "pairing_code": pairing_code})
    print(f"Valid code: {resp.status_code}")
    assert resp.status_code == 200

    # Test queue
    item_id = str(uuid4())
    payload = {
        "device_id": "test-device",
        "items": [
            {
                "id": item_id,
                "entity_type": "lost_person_report",
                "payload": {
                    "description": "Test",
                    "location": "Here"
                }
            }
        ]
    }
    resp = client.post("/sync/queue", json=payload)
    print(f"Queue insert: {resp.status_code}")
    assert resp.status_code == 200

    # Test duplicate
    resp2 = client.post("/sync/queue", json=payload)
    print(f"Queue duplicate: {resp2.status_code}")
    assert resp2.status_code == 200
    assert resp2.json()["accepted"][0]["status"] == "duplicate"

    # Test family status
    resp = client.get(f"/family/status?family_link_id={link_id}")
    print(f"Family status by link_id: {resp.status_code}")
    assert resp.status_code == 200

    resp = client.get(f"/family/status?device_id=test-device")
    print(f"Family status by device_id: {resp.status_code}")
    assert resp.status_code == 200

    print("All tests passed!")

if __name__ == "__main__":
    test_basic()