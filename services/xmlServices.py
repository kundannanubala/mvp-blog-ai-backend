import feedparser
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from asyncio import gather
from services.articleServices import save_processed_entries

async def scraper(link: str) -> str:
    """
    A dummy scraper function that processes a single feed entry link.
    """
    return f"{link} parsed"

async def summary(scrape_result: str) -> str:
    """
    A dummy summary function that processes the scraper result.
    """
    return f"Summary of {scrape_result}"

async def image(scrape_result: str) -> str:
    """
    A dummy image function that processes the scraper result.
    """
    return f"Image extracted from {scrape_result}"

async def blog(scrape_result: str) -> str:
    """
    A dummy blog function that processes the scraper result.
    """
    return f"Blog content from {scrape_result}"

async def keyword(scrape_result: str) -> str:
    """
    A dummy keyword function that processes the scraper result.
    """
    return f"Keywords extracted from {scrape_result}"

async def process_entry(entry, url):
    """
    Helper function to process a single entry concurrently
    """
    image_url = None
    if 'media_content' in entry and entry.media_content:
        image_url = entry.media_content[0]['url']
    
    # First get scrape result
    scrape_result = await scraper(entry.link)
    
    # Then process the remaining functions concurrently
    summary_result, image_result, blog_result, keyword_result = await gather(
        summary(scrape_result),
        image(scrape_result),
        blog(scrape_result),
        keyword(scrape_result)
    )
    
    return {
        'title': entry.title,
        'published': entry.get('published', 'No date available'),
        'link': entry.link,
        'source': url,
        'image_url': image_url,
        'scrape_result': scrape_result,
        'summary_result': summary_result,
        'image_result': image_result,
        'blog_result': blog_result,
        'keyword_result': keyword_result
    }

async def get_consolidated_todays_feeds(urls):
    """
    Parse a list of XML URLs and return a consolidated list of feeds published today.

    Args:
        urls (list): A list of XML feed URLs.

    Returns:
        list: A consolidated list of entries published today.
    """
    async def process_feed(url):
        feed = feedparser.parse(url)
        today = datetime.now().date()
        
        # Filter entries for today and process them concurrently
        today_entries = []
        for entry in feed.entries:
            if 'published_parsed' in entry:
                published_date = datetime(*entry.published_parsed[:6]).date()
                if published_date == today:
                    today_entries.append(process_entry(entry, url))
        
        if today_entries:
            return await gather(*today_entries)
        return []

    # Process all feeds concurrently
    all_entries = await gather(*[process_feed(url) for url in urls])
    flattened_entries = [entry for feed_entries in all_entries for entry in feed_entries]
    
    # Save processed entries to articles collection
    saved_articles = await save_processed_entries(flattened_entries)
    
    return flattened_entries

async def get_consolidated_feeds(urls):
    """
    Parse a list of XML URLs and return a consolidated list of all feeds.

    Args:
        urls (list): A list of XML feed URLs.

    Returns:
        list: A consolidated list of all entries.
    """
    async def process_feed(url):
        feed = feedparser.parse(url)
        # Process all entries in this feed concurrently
        entries = await gather(*[
            process_entry(entry, url) for entry in feed.entries
        ])
        return entries

    # Process all feeds concurrently
    all_entries = await gather(*[process_feed(url) for url in urls])
    flattened_entries = [entry for feed_entries in all_entries for entry in feed_entries]
    
    # Save processed entries to articles collection
    saved_articles = await save_processed_entries(flattened_entries)
    
    return flattened_entries

async def get_xml_urls_from_db():
    """
    Fetch XML URLs from the MongoDB collection.

    Returns:
        list: A list of dictionaries containing URL and metadata.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db['xml_urls']

    xml_urls_cursor = collection.find({}, {"_id": 0})
    xml_urls = await xml_urls_cursor.to_list(length=None)

    client.close()

    return xml_urls
