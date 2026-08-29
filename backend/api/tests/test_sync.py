from uuid import uuid4


def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_catalog_includes_source_and_last_updated(client) -> None:
    response = client.get("/sync/catalog")
    assert response.status_code == 200
    body = response.json()
    assert body["facilities"]
    for collection in body.values():
        for row in collection:
            assert row.get("source")
            assert row.get("last_updated")


def test_wari_scheduled_is_not_relabeled_live(client) -> None:
    response = client.get("/sync/catalog")
    for row in response.json()["wari_schedule"]:
        assert row["position_status"] == "scheduled"
        assert row["position_status"] != "live"
