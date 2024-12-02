from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from uuid import uuid4
from datetime import datetime
from services.xmlServices import *
from asyncio import gather

# Initialize the FastAPI router for handling XML-related endpoints
router = APIRouter()

class XmlUrlRequest(BaseModel):
    """
    Data model for the request body when adding XML URLs.

    Attributes:
        urls (Dict[str, str]): A dictionary where the key is the URL and the value is the domain.
    """
    urls: Dict[str, str]

@router.get("/")
async def get_xml_feeds():
    """
    Endpoint to fetch and consolidate XML feeds.

    This function retrieves all URLs from the database, separates them into today's and older URLs,
    fetches their feeds concurrently, and writes the consolidated feeds to a file.

    Returns:
        list: A list of all consolidated feeds.
    """
    # Retrieve all URLs with their metadata from the database
    xml_urls_data = await get_xml_urls_from_db()

    # Initialize lists to separate today's URLs from older URLs
    today = datetime.now().date()
    todays_urls = []
    older_urls = []

    # Categorize URLs based on their creation date
    for url_data in xml_urls_data:
        created_date = url_data["created_at"].date()
        if created_date == today:
            todays_urls.append(url_data["url"])
        else:
            older_urls.append(url_data["url"])
    print(f"Todays URLs: {todays_urls}")

    # Fetch feeds for both today's and older URLs concurrently
    todays_feeds, older_feeds = await gather(
        get_consolidated_todays_feeds(older_urls), get_consolidated_feeds(todays_urls)
    )

    # Combine all fetched feeds into a single list
    all_feeds = todays_feeds + older_feeds

    # Write the consolidated feeds to a text file
    with open("result.txt", "w") as file:
        for feed in all_feeds:
            file.write("Title: {}\n".format(feed["title"]))
            file.write("Published: {}\n".format(feed["published"]))
            file.write("Link: {}\n".format(feed["link"]))
            file.write("Source URL: {}\n\n".format(feed["source"]))
            file.write("-" * 50 + "\n")

    return all_feeds

@router.post("/add-urls")
async def add_xml_urls(xml_url_request: XmlUrlRequest):
    """
    Endpoint to add new XML URLs to the database.

    This function takes a list of URLs and their associated domains, checks for duplicates,
    and inserts new entries into the database.

    Args:
        xml_url_request (XmlUrlRequest): The request object containing URLs and domains.

    Returns:
        dict: A dictionary containing a success message, list of successful IDs, and any errors encountered.
    """
    # Create a new MongoDB client instance
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db["xml_urls"]

    results = []  # List to store successful insert IDs
    errors = []   # List to store error messages

    # Iterate over each URL and domain pair in the request
    for url, domain in xml_url_request.urls.items():
        try:
            # Check if the URL already exists in the database
            existing_url = await collection.find_one({"url": url})
            if existing_url:
                errors.append(f"URL already exists: {url}")
                continue

            # Insert the new URL and domain into the database
            result = await collection.insert_one(
                {
                    "url": url,
                    "domain": domain,
                    "id": f"{domain}_{uuid4()}",
                    "created_at": datetime.utcnow(),
                }
            )
            results.append(str(result.inserted_id))
        except Exception as e:
            errors.append(f"Error adding URL {url}: {str(e)}")

    # Close the MongoDB client connection
    client.close()

    return {
        "message": f"Added {len(results)} URLs successfully",
        "successful_ids": results,
        "errors": errors if errors else None,
    }

@router.get("/get-urls")
async def get_xml_urls():
    """
    Endpoint to retrieve all XML URLs from the database.

    This function fetches all stored URLs and their metadata from the database.

    Returns:
        list: A list of dictionaries containing URL data.
    """
    # Fetch all XML URLs from the database
    xml_urls_data = await get_xml_urls_from_db()
    return xml_urls_data
