from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from bson import ObjectId
from services.articleServices import get_article
import logging

# Initialize the FastAPI router for handling article-related endpoints
router = APIRouter()

@router.get("/")
async def get_articles():
    """
    Fetch all articles from the database.

    Returns:
        list: A list of articles.
    """
    return await get_article()

@router.get("/{id}")
async def get_article_by_id(id: str):
    """
    Fetch a single article by its ID.

    Args:
        id (str): The ID of the article to fetch.

    Returns:
        dict: The article data if found.

    Raises:
        HTTPException: If the ID format is invalid or the article is not found.
    """
    # Create a new MongoDB client instance
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db["articles"]

    try:
        logging.info(f"Fetching article with ID: {id}")
        
        # Validate the format of the provided ID
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID format")

        # Attempt to find the article in the database
        article = await collection.find_one({"_id": ObjectId(id)})
        if article is None:
            raise HTTPException(status_code=404, detail="Article not found")

        # Convert ObjectId to string for JSON serialization
        article["id"] = str(article["_id"])
        del article["_id"]

        return article
    except Exception as e:
        logging.error(f"Error fetching article: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Ensure the MongoDB client is closed after the operation
        client.close()
