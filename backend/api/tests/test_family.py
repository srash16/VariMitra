from uuid import uuid4

from app.security import hash_secret


def test_pairing_stores_hashes_only(client, repo) -> None:
    start = client.post(
        "/family/pair/start",
        json={"family_device_id": "family-1", "family_name": "Patil"},
    )
    assert start.status_code == 200
    payload = start.json()
    code = payload["pairing_code"]
    token = payload["qr_token"]
    link_id = payload["family_link_id"]

    stored = repo.family_links[link_id]
    assert code not in stored.values()
    assert token not in stored.values()
    assert stored["pairing_code_hash"] == hash_secret(code)
    assert stored["qr_token_hash"] == hash_secret(token)
    assert stored["pairing_code_hash"] != code
    assert "pairing_code" not in stored

    complete = client.post(
        "/family/pair/complete",
        json={"pilgrim_device_id": "pilgrim-1", "pairing_code": code},
    )
    assert complete.status_code == 200
    assert complete.json()["paired"] is True

    status = client.get("/family/status", params={"family_link_id": link_id})
    assert status.status_code == 200
    body = status.json()
    assert body["paired"] is True
    assert "cannot guarantee delivery" in body["note"].lower() or "queued" in body["note"].lower() or "last-known" in body["note"].lower()
