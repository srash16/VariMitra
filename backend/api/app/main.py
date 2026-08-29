from fastapi import FastAPI

from app.routers.family import router as family_router
from app.routers.health import router as health_router
from app.routers.sync import router as sync_router

app = FastAPI(
    title="VariMitra API",
    version="0.1.0",
    description=(
        "Necessary online layer for VariMitra: catalog sync, Family Link pairing "
        "(hashes only), and queued Lost & Found / SOS ingest. "
        "Does not run STT, LLM, or emergency calls."
    ),
)

app.include_router(health_router)
app.include_router(sync_router)
app.include_router(family_router)
