from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.deps import get_repo
from app.repo import Repository
from app.schemas import CatalogResponse, QueueRequest, QueueResponse

router = APIRouter(prefix="/sync", tags=["sync"])

QUEUE_NOTE = (
    "Accepted for server storage only. Offline reports stay queued until reconnect. "
    "This API does not confirm delivery to a remote family member. "
    "SOS ingest never places an emergency call."
)


@router.get("/catalog", response_model=CatalogResponse)
def catalog(
    since: datetime | None = Query(default=None),
    repo: Repository = Depends(get_repo),
) -> CatalogResponse:
    return repo.catalog_since(since)


@router.post("/queue", response_model=QueueResponse)
def ingest_queue(
    body: QueueRequest,
    repo: Repository = Depends(get_repo),
) -> QueueResponse:
    accepted = repo.ingest_queue(body.device_id, body.items)
    return QueueResponse(accepted=accepted, note=QUEUE_NOTE)
