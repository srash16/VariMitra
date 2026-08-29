from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from app.schemas import CatalogResponse, QueueItem


class Repository(Protocol):
    def catalog_since(self, since: datetime | None) -> CatalogResponse: ...

    def ingest_queue(self, device_id: str, items: list[QueueItem]) -> list[dict[str, Any]]: ...

    def pair_start(
        self,
        family_device_id: str,
        pairing_code: str,
        qr_token: str,
        family_name: str | None,
        emergency_contact: str | None,
    ) -> dict[str, Any]: ...

    def pair_complete(
        self,
        pilgrim_device_id: str,
        pairing_code: str | None,
        qr_token: str | None,
    ) -> dict[str, Any] | None: ...

    def family_status(
        self, family_link_id: UUID | None, device_id: str | None
    ) -> dict[str, Any] | None: ...
