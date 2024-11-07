import feedparser
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from asyncio import gather
from services.articleServices import save_processed_entries
from services.blogServices import generate_blog_post
from services.imageServices import generate_image_vertexai
from services.scrapeServices import scrape
from services.keywordServices import keyword_generation
import dotenv
dotenv.load_dotenv()
from groq import AsyncGroq
from services.summaryServices import summary
from datetime import timedelta
import os

# Configure Groq client
try:
    client = AsyncGroq(
        api_key=settings.GROQ_API_KEY
    )
except Exception as e:
    print(f"Error configuring Groq API: {str(e)}")

async def scraper(link: str) -> str:
    return await scrape(link)

async def summary(scrape_result: str) -> str:
    """
    Summarizes the scraped content using Groq's Mixtral model.
    Returns a concise summary while preserving key context.
    """
    # try:
    #     # Add exponential backoff retry logic
    #     max_retries = 3
    #     base_delay = 5  # seconds
        
    #     for attempt in range(max_retries):
    #         try:
    #             prompt = f"""Summarize the following text in approximately 100 words while preserving all key context and main points:

    #             {scrape_result}"""

    #             response = await client.chat.completions.create(
    #                 messages=[{"role": "user", "content": prompt}],
    #                 model="llama-3.1-70b-versatile",
    #                 temperature=0.5,
    #                 max_tokens=8000,
    #                 top_p=1,
    #             )
                
    #             if response.choices[0].message.content:
    #                 return response.choices[0].message.content.strip()
                    
    #         except Exception as e:
    #             if "rate_limit_exceeded" in str(e):
    #                 if attempt < max_retries - 1:
    #                     delay = base_delay * (2 ** attempt)  # Exponential backoff
    #                     await asyncio.sleep(delay)
    #                     continue
    #             raise e
                
    #     return "No summary generated"

    # except Exception as e:
    #     return f"Error generating summary: {str(e)}"
    try:
        import google.generativeai as genai
        
        # Configure Gemini API
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        
        # Initialize Gemini 1.5 Flash model
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Create prompt for summarization
        prompt = f"""Summarize the following text in approximately 100 words while preserving all key context and main points:

        {scrape_result}"""
        
        # Generate summary
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text.strip()
            
        return "No summary generated"
        
    except Exception as e:
        return f"Error generating summary: {str(e)}"    

async def image(summary_result: str) -> str:
    return await generate_image_vertexai(summary_result)


async def blog(scrape_result: str) -> str:
    # Await the result of the coroutine properly
    return await generate_blog_post(scrape_result)

async def keyword(scrape_result: str) -> str:
    return await keyword_generation(scrape_result)

async def process_entry(entry, url):
    """
    Helper function to process a single entry concurrently
    """
    image_url = None
    if 'media_content' in entry and entry.media_content:
        image_url = entry.media_content[0]['url']
    
    # First get scrape result
    scrape_result = await scraper(entry.link)
    
    # # # Then process the remaining functions concurrently
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
        today = datetime.now().date() - timedelta(days=1)
        
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
