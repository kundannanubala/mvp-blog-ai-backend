from fastapi import APIRouter
from services.articleServices import get_article
router = APIRouter()

@router.get("/")
async def get_articles():
    return await get_article()