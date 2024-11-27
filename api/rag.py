from fastapi import APIRouter, HTTPException
from services.ragServices import store_article_in_vector_db, fetch_articles_by_username

router = APIRouter()

@router.post("/store-article")
async def store_article(article_data: dict):
    try:
        result = await store_article_in_vector_db(article_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/fetch-articles")
async def fetch_articles(username: str):
    try:
        result = await fetch_articles_by_username(username)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
