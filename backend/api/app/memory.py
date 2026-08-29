from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from app.schemas import CatalogResponse, QueueItem, freshness
from app.security import hash_secret, pairing_expiry, utcnow


def _after(ts: datetime | None, since: datetime | None) -> bool:
    if since is None or ts is None:
        return True
    if ts.tzinfo is None and since.tzinfo is not None:
        ts = ts.replace(tzinfo=since.tzinfo)
    return ts > since


class MemoryRepository:
    """In-memory store for tests. Pairing secrets are hashed before insert."""

    def __init__(self) -> None:
        now = utcnow()
        self.facilities: list[dict[str, Any]] = [
            freshness(
                {
                    "id": str(uuid4()),
                    "name": "Demo water point",
                    "type": "water",
                    "source": "seed",
                    "last_updated": now,
                    "created_at": now,
                }
            )
        ]
        self.facility_updates: list[dict[str, Any]] = []
        self.wari_palkhis: list[dict[str, Any]] = [
            freshness(
                {
                    "id": str(uuid4()),
                    "name": "Dnyaneshwar Palkhi",
                    "source": "seed",
                    "created_at": now,
                    "last_updated": now,
                }
            )
        ]
        self.wari_route_segments: list[dict[str, Any]] = []
        self.wari_schedule: list[dict[str, Any]] = [
            freshness(
                {
                    "id": str(uuid4()),
                    "wari_year": 2026,
                    "schedule_date": "2026-06-15",
                    "expected_location": "Pune (scheduled halt)",
                    "position_status": "scheduled",
                    "source": "seed",
                    "last_updated": now,
                }
            )
        ]
        self.wari_major_dates: list[dict[str, Any]] = []
        self.local_information: list[dict[str, Any]] = []
        self.emergency_contacts: list[dict[str, Any]] = []
        self.family_links: dict[str, dict[str, Any]] = {}
        self.lost_person_reports: dict[str, dict[str, Any]] = {}
        self.sos_alerts: dict[str, dict[str, Any]] = {}
        self.facility_reports: dict[str, dict[str, Any]] = {}
        self.sync_events: dict[str, dict[str, Any]] = {}

    def catalog_since(self, since: datetime | None) -> CatalogResponse:
        def filt(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
            out = []
            for row in rows:
                stamped = freshness(row, "seed")
                if _after(stamped.get("last_updated"), since):
                    out.append(stamped)
            return out

        schedule = filt(self.wari_schedule)
        for row in schedule:
            # Never relabel scheduled as live.
            if row.get("position_status") == "scheduled":
                row["position_status"] = "scheduled"

        return CatalogResponse(
            facilities=filt(self.facilities),
            facility_updates=filt(self.facility_updates),
            wari_palkhis=filt(self.wari_palkhis),
            wari_route_segments=filt(self.wari_route_segments),
            wari_schedule=schedule,
            wari_major_dates=filt(self.wari_major_dates),
            local_information=filt(self.local_information),
            emergency_contacts=filt(self.emergency_contacts),
        )

    def ingest_queue(self, device_id: str, items: list[QueueItem]) -> list[dict[str, Any]]:
        now = utcnow()
        results: list[dict[str, Any]] = []
        stores = {
            "lost_person_report": self.lost_person_reports,
            "sos_alert": self.sos_alerts,
            "facility_report": self.facility_reports,
        }
        for item in items:
            key = str(item.id)
            store = stores[item.entity_type]
            if key in store:
                results.append(
                    {
                        "id": item.id,
                        "entity_type": item.entity_type,
                        "status": "duplicate",
                        "emergency_action_required": False,
                        "family_delivered": False,
                    }
                )
                continue
            record = {
                "id": key,
                "device_id": device_id,
                "reported_by_device_id": device_id,
                "payload": dict(item.payload),
                "client_created_at": item.client_created_at,
                "server_received_at": now,
                "status": item.payload.get("status", "missing" if item.entity_type == "lost_person_report" else "pending"),
                "family_link_id": item.payload.get("family_link_id"),
            }
            store[key] = record
            self.sync_events[key] = {
                "id": key,
                "device_id": device_id,
                "entity_type": item.entity_type,
                "entity_id": key,
                "operation": item.operation,
                "status": "synced",
                "synced_at": now,
            }
            results.append(
                {
                    "id": item.id,
                    "entity_type": item.entity_type,
                    "status": "synced",
                    "emergency_action_required": False,
                    "family_delivered": False,
                }
            )
        return results

    def pair_start(
        self,
        family_device_id: str,
        pairing_code: str,
        qr_token: str,
        family_name: str | None,
        emergency_contact: str | None,
    ) -> dict[str, Any]:
        link_id = uuid4()
        expires = pairing_expiry()
        self.family_links[str(link_id)] = {
            "id": str(link_id),
            "pilgrim_device_id": "",
            "family_device_id": family_device_id,
            "pairing_code_hash": hash_secret(pairing_code),
            "qr_token_hash": hash_secret(qr_token),
            "family_name": family_name,
            "emergency_contact": emergency_contact,
            "is_active": False,
            "paired_at": None,
            "expires_at": expires,
            "created_at": utcnow(),
        }
        return {"family_link_id": link_id, "expires_at": expires}

    def pair_complete(
        self,
        pilgrim_device_id: str,
        pairing_code: str | None,
        qr_token: str | None,
    ) -> dict[str, Any] | None:
        code_hash = hash_secret(pairing_code) if pairing_code else None
        qr_hash = hash_secret(qr_token) if qr_token else None
        now = utcnow()
        for link in self.family_links.values():
            expired = link["expires_at"] is not None and link["expires_at"] < now
            if expired:
                continue
            match_code = code_hash and link["pairing_code_hash"] == code_hash
            match_qr = qr_hash and link["qr_token_hash"] == qr_hash
            if match_code or match_qr:
                link["pilgrim_device_id"] = pilgrim_device_id
                link["is_active"] = True
                link["paired_at"] = now
                return {
                    "family_link_id": UUID(link["id"]),
                    "is_active": True,
                    "paired": True,
                }
        return None

    def family_status(
        self, family_link_id: UUID | None, device_id: str | None
    ) -> dict[str, Any] | None:
        link = None
        if family_link_id is not None:
            link = self.family_links.get(str(family_link_id))
        elif device_id:
            for candidate in self.family_links.values():
                if device_id in (candidate.get("pilgrim_device_id"), candidate.get("family_device_id")):
                    link = candidate
                    break
        if not link:
            return None
        reports = [
            row
            for row in self.lost_person_reports.values()
            if row.get("family_link_id") in (link["id"], UUID(link["id"]) if False else link["id"])
            or str(row.get("family_link_id")) == link["id"]
        ]
        delivery = "last_known" if link.get("is_active") else "queued"
        return {
            "family_link_id": UUID(link["id"]),
            "is_active": bool(link.get("is_active")),
            "paired": bool(link.get("paired_at")),
            "delivery": delivery,
            "lost_reports": reports,
        }
