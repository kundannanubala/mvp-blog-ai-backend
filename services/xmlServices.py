import aiohttp
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from asyncio import gather
from services.articleServices import save_processed_entries
import google.generativeai as genai
import os
from typing import Optional
import asyncio
from groq import AsyncGroq

# Configure Groq client
try:
    client = AsyncGroq(
        api_key=settings.GROQ_API_KEY
    )
except Exception as e:
    print(f"Error configuring Groq API: {str(e)}")

async def scraper(link: str) -> str:
    """
    Scrapes and cleans blog content from the given URL.
    Returns only the cleaned content text.
    """
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_NAME]
        collection = db['scraped_content']
        
        # Check if URL already scraped
        existing = await collection.find_one({"url": link})
        if existing:
            return existing['content']
            
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 
                                                'meta', 'input', 'button', 'form', 'iframe',
                                                'noscript', 'svg', 'path', 'aside', '.sidebar',
                                                '.advertisement', '.social-share', '.comments']):
                        element.decompose()
                    
                    # Find main content
                    main_content = None
                    for selector in ['article', 'main', '.post-content', '.entry-content', 
                                   '.blog-content', '.article-content', '#main-content']:
                        main_content = soup.select_one(selector)
                        if main_content:
                            break
                    
                    content_soup = main_content if main_content else soup.body
                    
                    if content_soup:
                        # Extract only meaningful paragraphs and headings
                        paragraphs = content_soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                        text_content = []
                        
                        for p in paragraphs:
                            text = p.get_text(strip=True)
                            if text and len(text) > 20:  # Only keep substantial paragraphs
                                # Clean the text
                                text = ' '.join(text.split())  # Normalize whitespace
                                text = text.replace('Click here', '')
                                text = text.replace('Subscribe now', '')
                                text = text.replace('Advertisement', '')
                                text_content.append(text)
                        
                        # Join paragraphs with double newlines for readability
                        scrape_result = '\n\n'.join(text_content)
                        
                        if scrape_result:
                            # Store in MongoDB
                            await collection.insert_one({
                                "url": link,
                                "content": scrape_result,
                                "scraped_at": datetime.utcnow()
                            })
                            return scrape_result
                return "No meaningful content found"
                    
    except Exception as e:
        return f"Error scraping {link}: {str(e)}"
    finally:
        client.close()

async def summary(scrape_result: str) -> str:
    """
    Summarizes the scraped content using Groq's Mixtral model.
    Returns a concise summary while preserving key context.
    """
    try:
        prompt = f"""Summarize the following text in approximately 100 words while preserving all key context and main points:

        {scrape_result}"""

        # Generate summary using Mixtral model
        response = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
        )
        
        if response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        return "No summary generated"

    except Exception as e:
        return f"Error generating summary: {str(e)}"

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
