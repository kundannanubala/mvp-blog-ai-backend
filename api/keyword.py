from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from models.keywords import KeywordList

router = APIRouter()

@router.post("/save-keywords")
async def save_keywords(keyword_request: KeywordList):
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db['keywords']

    try:
        # Store each keyword as a separate document
        documents = [{"keyword": keyword} for keyword in keyword_request.keywords]
        result = await collection.insert_many(documents)
        return {"message": "Keywords saved successfully", "ids": [str(id) for id in result.inserted_ids]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        client.close()

