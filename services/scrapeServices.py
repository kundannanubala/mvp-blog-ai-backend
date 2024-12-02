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

    This function performs the following steps:
    1. Connects to a MongoDB database to check if the URL has already been scraped.
    2. If not, it fetches the HTML content of the page using an HTTP GET request.
    3. Parses the HTML to remove unwanted elements and extract meaningful content.
    4. Cleans the extracted content by normalizing whitespace and removing specific unwanted phrases.
    5. Stores the cleaned content in the MongoDB database.
    6. Returns the cleaned content as a string.

    Args:
        link (str): The URL of the blog to scrape.

    Returns:
        str: The cleaned content text or an error message if scraping fails.
    """
    try:
        # Initialize MongoDB client and access the specified database and collection
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_NAME]
        collection = db["scraped_content"]

        # Check if the URL has already been scraped and stored in the database
        existing = await collection.find_one({"url": link})
        if existing:
            return existing["content"]

        # Create an HTTP session to fetch the page content
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                if response.status == 200:
                    # Parse the HTML content using BeautifulSoup
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Remove unwanted HTML elements that do not contribute to the main content
                    for element in soup.find_all(
                        [
                            "script", "style", "nav", "header", "footer", "meta",
                            "input", "button", "form", "iframe", "noscript", "svg",
                            "path", "aside", ".sidebar", ".advertisement",
                            ".social-share", ".comments",
                        ]
                    ):
                        element.decompose()

                    # Attempt to find the main content using common selectors
                    main_content = None
                    for selector in [
                        "article", "main", ".post-content", ".entry-content",
                        ".blog-content", ".article-content", "#main-content",
                    ]:
                        main_content = soup.select_one(selector)
                        if main_content:
                            break

                    # Use the main content if found, otherwise default to the body
                    content_soup = main_content if main_content else soup.body

                    if content_soup:
                        # Extract paragraphs and headings from the content
                        paragraphs = content_soup.find_all(
                            ["p", "h1", "h2", "h3", "h4", "h5", "h6"]
                        )
                        text_content = []

                        for p in paragraphs:
                            text = p.get_text(strip=True)
                            # Only keep paragraphs with substantial content
                            if text and len(text) > 20:
                                # Normalize whitespace and remove unwanted phrases
                                text = " ".join(text.split())
                                text = text.replace("Click here", "")
                                text = text.replace("Subscribe now", "")
                                text = text.replace("Advertisement", "")
                                text_content.append(text)

                        # Join paragraphs with double newlines for better readability
                        scrape_result = "\n\n".join(text_content)

                        if scrape_result:
                            # Store the cleaned content in the MongoDB collection
                            await collection.insert_one(
                                {
                                    "url": link,
                                    "content": scrape_result,
                                    "scraped_at": datetime.utcnow(),
                                }
                            )
                            return scrape_result
                return "No meaningful content found"

    except Exception as e:
        return f"Error scraping {link}: {str(e)}"
    finally:
        # Ensure the MongoDB client is closed after operation
        client.close()
