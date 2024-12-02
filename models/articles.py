from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class Article(BaseModel):
    """
    Data model for representing an article.

    Attributes:
        ID (str): The unique identifier for the article.
        title (str): The title of the article.
        published (str): The publication date of the article.
        link (str): The URL link to the article.
        source (str): The source or publisher of the article.
        image_url (Optional[str]): The URL of the image associated with the article, if available.
        scrape_result (str): The result of the scraping process for the article.
        keyword_result (dict): The result of the keyword extraction process for the article.
        description (str): A brief description of the article.
        summary (Optional[str]): A summary of the article, if available.
        created_at (datetime): The timestamp when the article record was created, defaults to the current UTC time.
    """
    ID: str  # Unique identifier for the article
    title: str  # Title of the article
    published: str  # Publication date of the article
    link: str  # URL link to the article
    source: str  # Source or publisher of the article
    image_url: Optional[str]  # URL of the image associated with the article, if available
    scrape_result: str  # Result of the scraping process for the article
    keyword_result: dict  # Result of the keyword extraction process for the article
    description: str  # Brief description of the article
    summary: Optional[str]  # Summary of the article, if available
    created_at: datetime = datetime.utcnow()  # Timestamp when the article record was created, defaults to current UTC time
