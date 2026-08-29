from functools import lru_cache
import os

from app.memory import MemoryRepository
from app.postgres import PostgresRepository
from app.repo import Repository


@lru_cache
def get_repo() -> Repository:
    """Prefer Postgres; fall back to memory when DB is unreachable or forced."""
    if os.getenv("VARIMITRA_USE_MEMORY", "").lower() in {"1", "true", "yes"}:
        return MemoryRepository()
    try:
        repo = PostgresRepository()
        # Probe so we fail fast and fall back when Docker/Postgres is down.
        with repo._connect() as conn:
            conn.execute("select 1")
        return repo
    except Exception:
        return MemoryRepository()
