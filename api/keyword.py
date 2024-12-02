from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from models.keywords import KeywordList

# Initialize the FastAPI router for handling keyword-related endpoints
router = APIRouter()

@router.post("/save-keywords")
async def save_keywords(keyword_request: KeywordList):
    """
    Endpoint to save a list of keywords to the database.

    This function takes a list of keywords from the request body and stores each keyword
    as a separate document in the 'keywords' collection of the MongoDB database.

    Args:
        keyword_request (KeywordList): The request object containing a list of keywords to be saved.

    Returns:
        dict: A dictionary containing a success message and a list of IDs of the inserted documents.

    Raises:
        HTTPException: If an error occurs during the database operation, a 500 status code is returned
                       with the error details.
    """
    # Create a new MongoDB client instance
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db["keywords"]

    try:
        # Prepare documents for each keyword to be inserted into the database
        documents = [{"keyword": keyword} for keyword in keyword_request.keywords]
        
        # Insert the documents into the 'keywords' collection
        result = await collection.insert_many(documents)
        
        # Return a success message along with the IDs of the inserted documents
        return {
            "message": "Keywords saved successfully",
            "ids": [str(id) for id in result.inserted_ids],
        }
    except Exception as e:
        # Raise an HTTPException with a 500 status code if an error occurs
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Ensure the MongoDB client is closed after the operation
        client.close()
