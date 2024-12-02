from fastapi import APIRouter, HTTPException
from services.ragServices import store_article_in_vector_db, fetch_articles_by_username
from pydantic import BaseModel

# Initialize the FastAPI router for handling RAG-related endpoints
router = APIRouter()

class ArticleData(BaseModel):
    """
    Data model for the article data to be stored in the vector database.

    Attributes:
        title (str): The title of the article.
        content (str): The main content of the article.
        metadata (dict): Additional metadata related to the article, defaulting to an empty dictionary.
    """
    title: str
    content: str
    metadata: dict = {}

@router.post("/store-article")
async def store_article(article_data: ArticleData):
    """
    Endpoint to store an article in the vector database.

    This function takes article data, converts it to a dictionary, and stores it in the vector database.

    Args:
        article_data (ArticleData): The article data to be stored.

    Returns:
        dict: The result of the storage operation.

    Raises:
        HTTPException: If an error occurs during the storage process, a 500 status code is returned
                       with the error details.
    """
    try:
        # Convert the article data to a dictionary and store it in the vector database
        result = await store_article_in_vector_db(article_data.dict())
        return result
    except Exception as e:
        # Raise an HTTPException with a 500 status code if an error occurs
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fetch-articles")
async def fetch_articles(username: str):
    """
    Endpoint to fetch articles associated with a specific username.

    This function retrieves articles from the vector database that are linked to the provided username.

    Args:
        username (str): The username whose articles are to be fetched.

    Returns:
        list: A list of articles associated with the username.

    Raises:
        HTTPException: If an error occurs during the fetch process, a 500 status code is returned
                       with the error details.
    """
    try:
        # Fetch articles from the vector database using the provided username
        result = await fetch_articles_by_username(username)
        return result
    except Exception as e:
        # Raise an HTTPException with a 500 status code if an error occurs
        raise HTTPException(status_code=500, detail=str(e))
