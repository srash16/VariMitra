#!/usr/bin/env python3
"""Test to check if pairing code can be reused (loophole in MemoryRepository)."""

from fastapi.testclient import TestClient
from app.main import app
from app.memory import MemoryRepository
from app.deps import get_repo

# Override dependency to use a single MemoryRepository instance
repo = MemoryRepository()
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
# This should fail if the implementation correctly prevents code reuse.
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

# Determine if the loophole exists:
# If the second attempt succeeded (status 200) and the pilgrim_device_id changed to pilgrim-2,
# then the loophole exists (code can be reused to hijack the link).
# If the second attempt failed (status 404) and the link remains bound to pilgrim-1,
# then the loophole is fixed.

if resp_second.status_code == 200:
    print("\n❌ LOOPHOLE DETECTED: Pairing code can be reused to hijack the link.")
    if link_obj.get('pilgrim_device_id') == 'pilgrim-2':
        print("   The link has been hijacked by pilgrim-2.")
else:
    print("\n✓ No loophole detected: Pairing code cannot be reused after successful pairing.")

# Clean up
app.dependency_overrides.clear()