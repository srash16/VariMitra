from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.deps import get_repo
from app.main import app
from app.memory import MemoryRepository


@pytest.fixture
def repo() -> MemoryRepository:
    return MemoryRepository()


@pytest.fixture
def client(repo: MemoryRepository) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_repo] = lambda: repo
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
