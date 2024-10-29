import feedparser
from datetime import datetime

# Get consolidated todays feeds
async def get_consolidated_todays_feeds(urls):
    """
    Parse a list of XML URLs and return a consolidated list of feeds published today.

    Args:
        urls (list): A list of XML feed URLs.

    Returns:
        list: A consolidated list of entries published today.
    """
    consolidated_entries = []
    today = datetime.now().date()

    for url in urls:
        feed = feedparser.parse(url)

        # Extract items published today
        for entry in feed.entries:
            if 'published_parsed' in entry:
                published_date = datetime(*entry.published_parsed[:6]).date()
                if published_date == today:
                    # Add the entry to the consolidated list
                    consolidated_entries.append({
                        'title': entry.title,
                        'published': entry.published,
                        'link': entry.link,
                        'source': url  # Include the source URL
                    })

    return consolidated_entries

from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

async def get_xml_urls_from_db():
    """
    Fetch XML URLs from the MongoDB collection.

    Returns:
        list: A list of XML URLs.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db['xml_urls']

    xml_urls_cursor = collection.find({}, {"url": 1, "_id": 0})
    xml_urls = [doc["url"] for doc in await xml_urls_cursor.to_list(length=None)]

    client.close()

    return xml_urls
