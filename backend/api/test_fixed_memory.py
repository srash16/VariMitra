#!/usr/bin/env python3
"""Test that shows fixing the MemoryRepository closes the pairing code loophole."""

from fastapi.testclient import TestClient
from app.main import app
from app.memory import MemoryRepository
from app.deps import get_repo
from app.security import hash_secret
from typing import Any, Optional
from uuid import UUID
from datetime import datetime, timezone

# Create a fixed version of MemoryRepository that matches PostgresRepository behavior
class FixedMemoryRepository(MemoryRepository):
    def pair_complete(
        self,
        pilgrim_device_id: str,
        pairing_code: str | None,
        qr_token: str | None,
    ) -> Optional[dict[str, Any]]:
        code_hash = hash_secret(pairing_code) if pairing_code else None
        qr_hash = hash_secret(qr_token) if qr_token else None
        now = datetime.now(timezone.utc)  # Use timezone-aware UTC to match utcnow()
        for link in self.family_links.values():
            expired = link["expires_at"] is not None and link["expires_at"] < now
            if expired or link.get("is_active"):  # <-- ADD THIS LINE to skip active links
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

# Override dependency to use the fixed repository
repo = FixedMemoryRepository()
app.dependency_overrides[get_repo] = lambda: repo

client = TestClient(app)

# Step 1: Start a pairing
resp_start = client.post("/family/pair/start", json={
    "family_device_id": "test-device",
    "family_name": "Test Family"
})
assert resp_start.status_code == 200
data_start = resp_start.json()
link_id = data_start["family_link_id"]
pairing_code = data_start["pairing_code"]
print(f"Started pairing: link_id={link_id}, code={pairing_code}")

# Step 2: First pairing completion (should succeed)
resp_first = client.post("/family/pair/complete", json={
    "pilgrim_device_id": "pilgrim-1",
    "pairing_code": pairing_code
})
print(f"First pairing attempt: status={resp_first.status_code}")
if resp_first.status_code != 200:
    print(f"  Response: {resp_first.text}")
else:
    print(f"  Response: {resp_first.json()}")
assert resp_first.status_code == 200
assert resp_first.json()["paired"] is True

# Step 3: Second pairing completion with the same code but different pilgrim device
# This should fail now because we skip active links.
resp_second = client.post("/family/pair/complete", json={
    "pilgrim_device_id": "pilgrim-2",
    "pairing_code": pairing_code
})
print(f"Second pairing attempt (different pilgrim): status={resp_second.status_code}")
if resp_second.status_code != 200:
    print(f"  Response: {resp_second.text}")
else:
    print(f"  Response: {resp_second.json()}")

# Check the link state in the repository after both attempts
link_obj = repo.family_links[link_id]
print(f"Link state after attempts:")
print(f"  pilgrim_device_id: {link_obj.get('pilgrim_device_id')}")
print(f"  is_active: {link_obj.get('is_active')}")
print(f"  paired_at: {link_obj.get('paired_at')}")

# Determine if the loophole is fixed:
# If the second attempt failed (status 404) and the link remains bound to pilgrim-1,
# then the loophole is fixed.

if resp_second.status_code == 404:
    print("\n✓ Loophole is FIXED: Pairing code cannot be reused after successful pairing.")
    if link_obj.get('pilgrim_device_id') == 'pilgrim-1':
        print("   The link remains bound to the original pilgrim-1.")
else:
    print("\n❌ Loophole still present: Pairing code can be reused.")

# Clean up
app.dependency_overrides.clear()