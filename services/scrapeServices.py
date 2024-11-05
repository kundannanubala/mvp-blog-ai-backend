import os
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from core.config import settings

load_dotenv()

async def scrape(link: str) -> str:
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
