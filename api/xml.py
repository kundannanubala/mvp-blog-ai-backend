from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from uuid import uuid4
from datetime import datetime
from services.xmlServices import *

router = APIRouter()

# Define a Pydantic model for the request body
class XmlUrlRequest(BaseModel):
    url: str
    domain: str

@router.get("/")
async def get_xml_feeds():
    xml_urls = await get_xml_urls_from_db()

    todays_feeds = get_consolidated_todays_feeds(xml_urls)
    with open("result.txt", "w") as file:
        for feed in todays_feeds:
            file.write("Title: {}\n".format(feed['title']))
            file.write("Published: {}\n".format(feed['published']))
            file.write("Link: {}\n".format(feed['link']))
            file.write("Source URL: {}\n\n".format(feed['source']))
            file.write("-" * 50 + "\n")

    return todays_feeds

@router.post("/add-url")
async def add_xml_url(xml_url_request: XmlUrlRequest):
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db['xml_urls']
    

    # Check if the URL already exists
    existing_url = await collection.find_one({"url": xml_url_request.url})
    if existing_url:
        raise HTTPException(status_code=400, detail="URL already exists")

    # Insert the new URL and domain
    result = await collection.insert_one({
        "url": xml_url_request.url,
        "domain": xml_url_request.domain,
        "id": f"{xml_url_request.domain}_{uuid4()}",
        "created_at": datetime.utcnow()  # Ensure this line is included
    })

    # Close the MongoDB connection
    client.close()

    return {"message": "URL added successfully", "id": str(result.inserted_id)}


