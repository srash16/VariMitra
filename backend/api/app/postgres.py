from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json

from app.config import settings
from app.schemas import CatalogResponse, QueueItem, freshness
from app.security import hash_secret, pairing_expiry, utcnow

CATALOG_QUERIES = {
    "facilities": "select * from facilities where (%(since)s is null or last_updated > %(since)s)",
    "facility_updates": "select * from facility_updates where (%(since)s is null or updated_at > %(since)s)",
    "wari_palkhis": "select * from wari_palkhis where (%(since)s is null or created_at > %(since)s)",
    "wari_route_segments": "select * from wari_route_segments where (%(since)s is null or created_at > %(since)s)",
    "wari_schedule": "select * from wari_schedule where (%(since)s is null or last_updated > %(since)s)",
    "wari_major_dates": "select * from wari_major_dates where (%(since)s is null or last_updated > %(since)s)",
    "local_information": "select * from local_information where (%(since)s is null or last_updated > %(since)s)",
    "emergency_contacts": "select * from emergency_contacts where (%(since)s is null or last_updated > %(since)s)",
}

ENTITY_TABLE = {
    "lost_person_report": "lost_person_reports",
    "sos_alert": "sos_alerts",
    "facility_report": "facility_reports",
}


def _jsonable(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, UUID):
            out[key] = str(value)
        elif isinstance(value, datetime):
            out[key] = value
        else:
            out[key] = value
    return out


class PostgresRepository:
    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(settings.database_url, row_factory=dict_row)

    def catalog_since(self, since: datetime | None) -> CatalogResponse:
        params = {"since": since}
        with self._connect() as conn:
            bundles: dict[str, list[dict[str, Any]]] = {}
            for name, sql in CATALOG_QUERIES.items():
                rows = conn.execute(sql, params).fetchall()
                stamped = [freshness(_jsonable(row), "unknown") for row in rows]
                if name == "wari_schedule":
                    for row in stamped:
                        # Pass position_status through unchanged.
                        row["position_status"] = row.get("position_status")
                bundles[name] = stamped
        return CatalogResponse(**bundles)

    def ingest_queue(self, device_id: str, items: list[QueueItem]) -> list[dict[str, Any]]:
        now = utcnow()
        results: list[dict[str, Any]] = []
        with self._connect() as conn:
            for item in items:
                table = ENTITY_TABLE[item.entity_type]
                existing = conn.execute(
                    f"select id from {table} where id = %(id)s",  # noqa: S608
                    {"id": item.id},
                ).fetchone()
                if existing:
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
                payload = dict(item.payload)
                payload.setdefault("id", item.id)
                if item.entity_type == "lost_person_report":
                    conn.execute(
                        """
                        insert into lost_person_reports (
                          id, family_link_id, reported_by_device_id, person_name, age, gender,
                          description, last_seen_location, latitude, longitude, photo_url,
                          contact_number, status, client_created_at, server_received_at
                        ) values (
                          %(id)s, %(family_link_id)s, %(reported_by_device_id)s, %(person_name)s,
                          %(age)s, %(gender)s, %(description)s, %(last_seen_location)s,
                          %(latitude)s, %(longitude)s, %(photo_url)s, %(contact_number)s,
                          %(status)s, %(client_created_at)s, %(server_received_at)s
                        )
                        """,
                        {
                            "id": item.id,
                            "family_link_id": payload.get("family_link_id"),
                            "reported_by_device_id": device_id,
                            "person_name": payload.get("person_name"),
                            "age": payload.get("age"),
                            "gender": payload.get("gender"),
                            "description": payload.get("description"),
                            "last_seen_location": payload.get("last_seen_location")
                            or payload.get("location"),
                            "latitude": payload.get("latitude"),
                            "longitude": payload.get("longitude"),
                            "photo_url": payload.get("photo_url"),
                            "contact_number": payload.get("contact_number"),
                            "status": payload.get("status") or "missing",
                            "client_created_at": item.client_created_at,
                            "server_received_at": now,
                        },
                    )
                elif item.entity_type == "sos_alert":
                    conn.execute(
                        """
                        insert into sos_alerts (
                          id, device_id, family_link_id, latitude, longitude, location_name,
                          emergency_type, message, status, emergency_action, action_result,
                          client_created_at
                        ) values (
                          %(id)s, %(device_id)s, %(family_link_id)s, %(latitude)s, %(longitude)s,
                          %(location_name)s, %(emergency_type)s, %(message)s, %(status)s,
                          %(emergency_action)s, %(action_result)s, %(client_created_at)s
                        )
                        """,
                        {
                            "id": item.id,
                            "device_id": device_id,
                            "family_link_id": payload.get("family_link_id"),
                            "latitude": payload.get("latitude"),
                            "longitude": payload.get("longitude"),
                            "location_name": payload.get("location_name"),
                            "emergency_type": payload.get("emergency_type") or "general",
                            "message": payload.get("message"),
                            "status": payload.get("status") or "pending",
                            "emergency_action": payload.get("emergency_action"),
                            "action_result": payload.get("action_result"),
                            "client_created_at": item.client_created_at,
                        },
                    )
                else:
                    conn.execute(
                        """
                        insert into facility_reports (
                          id, facility_id, reported_by_device_id, report_type, description,
                          photo_url, status
                        ) values (
                          %(id)s, %(facility_id)s, %(reported_by_device_id)s, %(report_type)s,
                          %(description)s, %(photo_url)s, %(status)s
                        )
                        """,
                        {
                            "id": item.id,
                            "facility_id": payload.get("facility_id"),
                            "reported_by_device_id": device_id,
                            "report_type": payload.get("report_type") or "other",
                            "description": payload.get("description"),
                            "photo_url": payload.get("photo_url"),
                            "status": payload.get("status") or "pending",
                        },
                    )
                conn.execute(
                    """
                    insert into sync_events (
                      id, device_id, entity_type, entity_id, operation, payload, status,
                      client_created_at, synced_at
                    ) values (
                      %(id)s, %(device_id)s, %(entity_type)s, %(entity_id)s, %(operation)s,
                      %(payload)s, 'synced', %(client_created_at)s, %(synced_at)s
                    )
                    """,
                    {
                        "id": item.id,
                        "device_id": device_id,
                        "entity_type": item.entity_type,
                        "entity_id": item.id,
                        "operation": item.operation,
                        "payload": Json(payload),
                        "client_created_at": item.client_created_at,
                        "synced_at": now,
                    },
                )
                results.append(
                    {
                        "id": item.id,
                        "entity_type": item.entity_type,
                        "status": "synced",
                        "emergency_action_required": False,
                        "family_delivered": False,
                    }
                )
            conn.commit()
        return results

    def pair_start(
        self,
        family_device_id: str,
        pairing_code: str,
        qr_token: str,
        family_name: str | None,
        emergency_contact: str | None,
    ) -> dict[str, Any]:
        expires = pairing_expiry()
        with self._connect() as conn:
            row = conn.execute(
                """
                insert into family_links (
                  pilgrim_device_id, family_device_id, pairing_code_hash, qr_token_hash,
                  family_name, emergency_contact, is_active, expires_at
                ) values (
                  '', %(family_device_id)s, %(pairing_code_hash)s, %(qr_token_hash)s,
                  %(family_name)s, %(emergency_contact)s, false, %(expires_at)s
                )
                returning id, expires_at
                """,
                {
                    "family_device_id": family_device_id,
                    "pairing_code_hash": hash_secret(pairing_code),
                    "qr_token_hash": hash_secret(qr_token),
                    "family_name": family_name,
                    "emergency_contact": emergency_contact,
                    "expires_at": expires,
                },
            ).fetchone()
            conn.commit()
        assert row is not None
        return {"family_link_id": row["id"], "expires_at": row["expires_at"]}

    def pair_complete(
        self,
        pilgrim_device_id: str,
        pairing_code: str | None,
        qr_token: str | None,
    ) -> dict[str, Any] | None:
        now = utcnow()
        code_hash = hash_secret(pairing_code) if pairing_code else None
        qr_hash = hash_secret(qr_token) if qr_token else None
        with self._connect() as conn:
            row = conn.execute(
                """
                select * from family_links
                where is_active = false
                  and (expires_at is null or expires_at > %(now)s)
                  and (
                    (%(code_hash)s is not null and pairing_code_hash = %(code_hash)s)
                    or (%(qr_hash)s is not null and qr_token_hash = %(qr_hash)s)
                  )
                limit 1
                """,
                {"now": now, "code_hash": code_hash, "qr_hash": qr_hash},
            ).fetchone()
            if not row:
                return None
            conn.execute(
                """
                update family_links
                set pilgrim_device_id = %(pilgrim_device_id)s,
                    is_active = true,
                    paired_at = %(now)s
                where id = %(id)s
                """,
                {
                    "pilgrim_device_id": pilgrim_device_id,
                    "now": now,
                    "id": row["id"],
                },
            )
            conn.commit()
        return {
            "family_link_id": row["id"],
            "is_active": True,
            "paired": True,
        }

    def family_status(
        self, family_link_id: UUID | None, device_id: str | None
    ) -> dict[str, Any] | None:
        with self._connect() as conn:
            if family_link_id is not None:
                link = conn.execute(
                    "select * from family_links where id = %(id)s",
                    {"id": family_link_id},
                ).fetchone()
            elif device_id:
                link = conn.execute(
                    """
                    select * from family_links
                    where pilgrim_device_id = %(device_id)s
                       or family_device_id = %(device_id)s
                    order by created_at desc
                    limit 1
                    """,
                    {"device_id": device_id},
                ).fetchone()
            else:
                return None
            if not link:
                return None
            reports = conn.execute(
                "select * from lost_person_reports where family_link_id = %(id)s",
                {"id": link["id"]},
            ).fetchall()
        delivery = "last_known" if link.get("is_active") else "queued"
        return {
            "family_link_id": link["id"],
            "is_active": bool(link.get("is_active")),
            "paired": link.get("paired_at") is not None,
            "delivery": delivery,
            "lost_reports": [_jsonable(row) for row in reports],
        }
