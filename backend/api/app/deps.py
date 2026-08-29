from functools import lru_cache

from app.memory import MemoryRepository
from app.postgres import PostgresRepository
from app.repo import Repository


@lru_cache
def get_repo() -> Repository:
    try:
        return PostgresRepository()
    except Exception:
        return MemoryRepository()
