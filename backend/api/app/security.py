from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.config import settings

PAIRING_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def hash_secret(value: str) -> str:
    normalized = value.strip().upper()
    payload = f"{settings.pairing_pepper}:{normalized}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def generate_pairing_code(length: int = 6) -> str:
    return "".join(secrets.choice(PAIRING_ALPHABET) for _ in range(length))


def generate_qr_token() -> str:
    return secrets.token_urlsafe(24)


def pairing_expiry() -> datetime:
    return utcnow() + timedelta(hours=settings.pairing_ttl_hours)


def new_id() -> UUID:
    return uuid4()
