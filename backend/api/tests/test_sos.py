from uuid import uuid4


def test_sos_ingest_does_not_place_emergency_call(client) -> None:
    sos_id = str(uuid4())
    response = client.post(
        "/sync/queue",
        json={
            "device_id": "pilgrim-1",
            "items": [
                {
                    "id": sos_id,
                    "entity_type": "sos_alert",
                    "operation": "insert",
                    "payload": {
                        "latitude": 18.52,
                        "longitude": 73.85,
                        "emergency_type": "general",
                    },
                }
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"][0]["emergency_action_required"] is False
    assert body["accepted"][0]["family_delivered"] is False
    assert "never places an emergency call" in body["note"].lower()


def test_health_and_catalog_do_not_require_sos(client) -> None:
    assert client.get("/health").status_code == 200
    assert client.get("/sync/catalog").status_code == 200


def test_queue_is_idempotent(client) -> None:
    item_id = str(uuid4())
    payload = {
        "device_id": "pilgrim-1",
        "items": [
            {
                "id": item_id,
                "entity_type": "lost_person_report",
                "payload": {"description": "red shirt", "location": "Pune halt"},
            }
        ],
    }
    first = client.post("/sync/queue", json=payload)
    second = client.post("/sync/queue", json=payload)
    assert first.json()["accepted"][0]["status"] == "synced"
    assert second.json()["accepted"][0]["status"] == "duplicate"
    assert first.json()["accepted"][0]["family_delivered"] is False
