from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """Check the health of the system components."""
    try:
        # Check MongoDB connection
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        await client.admin.command('ping')
        client.close()

        return {
            "status": "healthy",
            "components": {
                "mongodb": "connected",
                "api": "running"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"System health check failed: {str(e)}"
        ) 