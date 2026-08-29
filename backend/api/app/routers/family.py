from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.deps import get_repo
from app.repo import Repository
from app.schemas import (
    FamilyStatusResponse,
    PairCompleteRequest,
    PairCompleteResponse,
    PairStartRequest,
    PairStartResponse,
)
from app.security import generate_pairing_code, generate_qr_token

router = APIRouter(prefix="/family", tags=["family"])

STATUS_NOTE = (
    "Shows last-known or queued family state. "
    "An offline phone cannot guarantee delivery to a remote family member."
)


@router.post("/pair/start", response_model=PairStartResponse)
def pair_start(
    body: PairStartRequest,
    repo: Repository = Depends(get_repo),
) -> PairStartResponse:
    pairing_code = generate_pairing_code()
    qr_token = generate_qr_token()
    created = repo.pair_start(
        family_device_id=body.family_device_id,
        pairing_code=pairing_code,
        qr_token=qr_token,
        family_name=body.family_name,
        emergency_contact=body.emergency_contact,
    )
    return PairStartResponse(
        family_link_id=created["family_link_id"],
        pairing_code=pairing_code,
        qr_token=qr_token,
        expires_at=created["expires_at"],
    )


@router.post("/pair/complete", response_model=PairCompleteResponse)
def pair_complete(
    body: PairCompleteRequest,
    repo: Repository = Depends(get_repo),
) -> PairCompleteResponse:
    if not body.pairing_code and not body.qr_token:
        raise HTTPException(status_code=400, detail="pairing_code or qr_token is required")
    result = repo.pair_complete(
        pilgrim_device_id=body.pilgrim_device_id,
        pairing_code=body.pairing_code,
        qr_token=body.qr_token,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="pairing code not found or expired")
    return PairCompleteResponse(**result)


@router.get("/status", response_model=FamilyStatusResponse)
def family_status(
    family_link_id: UUID | None = Query(default=None),
    device_id: str | None = Query(default=None),
    repo: Repository = Depends(get_repo),
) -> FamilyStatusResponse:
    if family_link_id is None and not device_id:
        raise HTTPException(status_code=400, detail="family_link_id or device_id is required")
    result = repo.family_status(family_link_id, device_id)
    if result is None:
        raise HTTPException(status_code=404, detail="family link not found")
    return FamilyStatusResponse(**result, note=STATUS_NOTE)
