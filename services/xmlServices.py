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
import os
import aiohttp
from bs4 import BeautifulSoup
import vertexai
from vertexai.vision_models import ImageGenerationModel
from groq import Groq

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
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        
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
    """
    Generates an image based on the scraped content using Vertex AI.
    Returns the path to the locally saved image.
    """
    try:
        # Initialize Vertex AI
        vertexai.init(project="researchdevelopment-424002", location="us-central1")
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

        # Create a prompt based on the scraped content
        # Use first 500 characters of scrape_result to create context
        context = summary_result[:500]
        
        prompt = f"""
        Create a professional image based on this content: {context}
        
        Consider the following guidelines:
        1. The image should be visually appealing and relevant to the content
        2. Use a modern and professional art style
        3. Ensure the image is suitable for a professional audience
        4. Create a balanced composition
        5. Use appropriate lighting and colors
        """

        # Generate the image
        images = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            language="en",
            aspect_ratio="16:9",  # Using widescreen ratio for blog images
            safety_filter_level="block_some",
            person_generation="allow_all",
        )

        if images:
            # Create output directory if it doesn't exist
            output_folder = "generated_blog_images"
            os.makedirs(output_folder, exist_ok=True)

            # Generate unique filename using timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_folder, f"blog_image_{timestamp}.png")

            # Save the image locally
            images[0].save(location=output_file, include_generation_parameters=False)
            
            print(f"Generated and saved image to: {output_file}")
            return output_file

        return ""  # Return empty string if no image was generated

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return ""  # Return empty string on error


async def blog(scrape_result: str) -> str:
    # Await the result of the coroutine properly
    return await generate_blog_post(scrape_result)

async def keyword(scrape_result: str) -> str:
    """
    Extract relevant keywords from the blog content using Groq API.
    Uses the scrape result and metadata to generate keywords with maximum relevance.
    """

    # Initialize Groq client
    client = Groq()

    # Create prompt for keyword extraction
    prompt = f"""
    Please analyze this blog content and extract the most relevant keywords.
    Focus on technical terms, key concepts, and important topics.
    Format the output as a comma-separated list of keywords.
    
    Content to analyze:
    {scrape_result}
    """

    # Call Groq API for keyword extraction
    completion = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {
                "role": "system", 
                "content": "You are a keyword extraction specialist. Extract relevant keywords from content."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=256,
        top_p=1,
        stream=False
    )

    # Get keywords from response
    keywords = completion.choices[0].message.content.strip()
    
    return keywords

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
