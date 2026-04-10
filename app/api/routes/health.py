"""Health check endpoints for application monitoring and probes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", status_code=200)
async def health_check():
    """Returns a basic health status confirming the application runs."""
    return {"status": "ok"}
