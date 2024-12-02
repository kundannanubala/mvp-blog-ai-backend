from services.cleaningServices import HTMLCleaner
import os
from datetime import timedelta
from services.summaryServices import summary
from groq import AsyncGroq
import feedparser
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from asyncio import gather
from services.articleServices import save_processed_entries
from services.blogServices import generate_blog_post
from services.imageServices import generate_image_vertexai
from services.scrapeServices import scrape
from services.keywordServices import extract_matching_keywords
import dotenv

# Load environment variables from a .env file
dotenv.load_dotenv()

# Configure Groq client for keyword extraction
try:
    client = AsyncGroq(api_key=settings.GROQ_API_KEY)
except Exception as e:
    print(f"Error configuring Groq API: {str(e)}")

# Initialize the HTML cleaner for cleaning descriptions
html_cleaner = HTMLCleaner()

async def scraper(link: str) -> str:
    """
    Scrape the content from the given URL.

    Args:
        link (str): The URL to scrape.

    Returns:
        str: The scraped content as a string.
    """
    return await scrape(link)

async def keyword(scrape_result: str) -> dict:
    """
    Extract matching keywords from the scraped content.

    Args:
        scrape_result (str): The content from which to extract keywords.

    Returns:
        dict: A dictionary of keywords and their counts.
    """
    return await extract_matching_keywords(scrape_result)

async def process_entry(entry, url):
    """
    Process a single feed entry to extract and clean relevant information.

    This function scrapes the entry's link, extracts keywords, generates a summary,
    and cleans the description. It also handles media content if available.

    Args:
        entry: The feed entry to process.
        url: The source URL of the feed.

    Returns:
        dict: A dictionary containing processed entry data.
    """
    # Initialize image URL to None
    image_url = None
    # Check if media content is available and extract the first image URL
    if "media_content" in entry and entry.media_content:
        image_url = entry.media_content[0]["url"]

    # Scrape the content from the entry's link
    scrape_result = await scraper(entry.link)
    # Extract keywords from the scraped content
    keyword_result = await keyword(scrape_result)
    # Generate a summary of the scraped content
    summary_text = await summary(scrape_result)

    # Safely get and clean the description with a fallback mechanism
    description = getattr(entry, "description", "")
    cleaned_description = (
        await html_cleaner.clean_meta_description(description) if description else ""
    )

    # Return a dictionary with all processed data
    return {
        "title": entry.title,
        "published": entry.get("published", "No date available"),
        "link": entry.link,
        "source": url,
        "image_url": image_url,
        "scrape_result": scrape_result,
        "keyword_result": keyword_result,
        "summary": summary_text,
        "description": cleaned_description
        or description
        or "No description available",  # Triple fallback for description
    }

async def get_consolidated_todays_feeds(urls):
    """
    Parse a list of XML URLs and return a consolidated list of feeds published today.

    This function processes each feed URL to extract entries published today,
    processes them concurrently, and saves the results.

    Args:
        urls (list): A list of XML feed URLs.

    Returns:
        list: A consolidated list of entries published today.
    """
    async def process_feed(url):
        # Parse the feed from the given URL
        feed = feedparser.parse(url)
        # Calculate today's date
        today = datetime.now().date() - timedelta(days=1)

        # Initialize a list to hold today's entries
        today_entries = []
        # Filter entries for today's date
        for entry in feed.entries:
            if "published_parsed" in entry:
                published_date = datetime(*entry.published_parsed[:6]).date()
                if published_date == today:
                    today_entries.append(process_entry(entry, url))

        # Process today's entries concurrently if any
        if today_entries:
            return await gather(*today_entries)
        return []

    # Process all feeds concurrently
    all_entries = await gather(*[process_feed(url) for url in urls])
    # Flatten the list of entries
    flattened_entries = [
        entry for feed_entries in all_entries for entry in feed_entries
    ]

    # Save processed entries to the articles collection
    saved_articles = await save_processed_entries(flattened_entries)

    return flattened_entries

async def get_consolidated_feeds(urls):
    """
    Parse a list of XML URLs and return a consolidated list of all feeds.

    This function processes each feed URL to extract all entries and saves the results.

    Args:
        urls (list): A list of XML feed URLs.

    Returns:
        list: A consolidated list of all entries.
    """
    async def process_feed(url):
        # Parse the feed from the given URL
        feed = feedparser.parse(url)
        # Process all entries in this feed concurrently
        entries = await gather(*[process_entry(entry, url) for entry in feed.entries])
        return entries

    # Process all feeds concurrently
    all_entries = await gather(*[process_feed(url) for url in urls])
    # Flatten the list of entries
    flattened_entries = [
        entry for feed_entries in all_entries for entry in feed_entries
    ]

    # Save processed entries to the articles collection
    saved_articles = await save_processed_entries(flattened_entries)

    return flattened_entries

async def get_xml_urls_from_db():
    """
    Fetch XML URLs from the MongoDB collection.

    This function connects to the MongoDB database, retrieves all XML URLs,
    and returns them as a list of dictionaries.

    Returns:
        list: A list of dictionaries containing URL and metadata.
    """
    # Initialize MongoDB client and access the database and collection
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db["xml_urls"]

    # Retrieve all XML URLs from the collection
    xml_urls_cursor = collection.find({}, {"_id": 0})
    xml_urls = await xml_urls_cursor.to_list(length=None)

    # Close the MongoDB client
    client.close()

    return xml_urls
