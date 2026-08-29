from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


def freshness(row: dict[str, Any], source_fallback: str = "unknown") -> dict[str, Any]:
    """Every catalog record must expose source and last_updated."""
    out = dict(row)
    out["source"] = out.get("source") or source_fallback
    out["last_updated"] = (
        out.get("last_updated") or out.get("updated_at") or out.get("created_at")
    )
    return out


class CatalogResponse(BaseModel):
    facilities: list[dict[str, Any]]
    facility_updates: list[dict[str, Any]]
    wari_palkhis: list[dict[str, Any]]
    wari_route_segments: list[dict[str, Any]]
    wari_schedule: list[dict[str, Any]]
    wari_major_dates: list[dict[str, Any]]
    local_information: list[dict[str, Any]]
    emergency_contacts: list[dict[str, Any]]


class QueueItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    entity_type: Literal["lost_person_report", "sos_alert", "facility_report"]
    operation: Literal["insert", "update", "delete"] = "insert"
    client_created_at: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class QueueRequest(BaseModel):
    device_id: str
    items: list[QueueItem]


class QueueItemResult(BaseModel):
    id: UUID
    entity_type: str
    status: Literal["synced", "duplicate"]
    emergency_action_required: bool = False
    family_delivered: bool = False


class QueueResponse(BaseModel):
    accepted: list[QueueItemResult]
    note: str


class PairStartRequest(BaseModel):
    family_device_id: str
    family_name: str | None = None
    emergency_contact: str | None = None


class PairStartResponse(BaseModel):
    family_link_id: UUID
    pairing_code: str
    qr_token: str
    expires_at: datetime
    note: str = "Show this code once. The server stores hashes only."


class PairCompleteRequest(BaseModel):
    pilgrim_device_id: str
    pairing_code: str | None = None
    qr_token: str | None = None


class PairCompleteResponse(BaseModel):
    family_link_id: UUID
    is_active: bool
    paired: bool


class FamilyStatusResponse(BaseModel):
    family_link_id: UUID
    is_active: bool
    paired: bool
    delivery: Literal["last_known", "queued", "unknown"]
    lost_reports: list[dict[str, Any]]
    note: str
