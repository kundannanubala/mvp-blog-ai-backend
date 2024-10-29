from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from uuid import uuid4
from datetime import datetime
from services.xmlServices import *
from asyncio import gather

router = APIRouter()

class XmlUrlRequest(BaseModel):
    urls: Dict[str, str]  # Key is URL, Value is domain

@router.get("/")
async def get_xml_feeds():
    # Get all URLs with their metadata from DB
    xml_urls_data = await get_xml_urls_from_db()
    
    # Separate today's URLs and older URLs
    today = datetime.now().date()
    todays_urls = []
    older_urls = []
    
    for url_data in xml_urls_data:
        created_date = url_data['created_at'].date()
        if created_date == today:
            todays_urls.append(url_data['url'])
        else:
            older_urls.append(url_data['url'])
    print(f"Todays URLs: {todays_urls}")
    
    # Get feeds for both sets of URLs concurrently
    todays_feeds, older_feeds = await gather(
        get_consolidated_todays_feeds(older_urls),
        get_consolidated_feeds(todays_urls)
    )
    
    # Combine all feeds
    all_feeds = todays_feeds + older_feeds
    
    # Write to file
    with open("result.txt", "w") as file:
        for feed in all_feeds:
            file.write("Title: {}\n".format(feed['title']))
            file.write("Published: {}\n".format(feed['published']))
            file.write("Link: {}\n".format(feed['link']))
            file.write("Source URL: {}\n\n".format(feed['source']))
            file.write("-" * 50 + "\n")

    return all_feeds

@router.post("/add-urls")
async def add_xml_urls(xml_url_request: XmlUrlRequest):
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db['xml_urls']
    
    results = []
    errors = []

    for url, domain in xml_url_request.urls.items():
        try:
            existing_url = await collection.find_one({"url": url})
            if existing_url:
                errors.append(f"URL already exists: {url}")
                continue

            result = await collection.insert_one({
                "url": url,
                "domain": domain,
                "id": f"{domain}_{uuid4()}",
                "created_at": datetime.utcnow()
            })
            results.append(str(result.inserted_id))
        except Exception as e:
            errors.append(f"Error adding URL {url}: {str(e)}")

    client.close()

    return {
        "message": f"Added {len(results)} URLs successfully",
        "successful_ids": results,
        "errors": errors if errors else None
    }


