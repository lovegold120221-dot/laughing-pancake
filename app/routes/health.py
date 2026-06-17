from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health() -> dict:
    return {
        "provider": "Eburon AI",
        "status": "ok",
        "checked_at": datetime.now(UTC).isoformat(),
    }

