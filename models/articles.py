from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class Article(BaseModel):
    ID: str
    title: str
    published: str
    link: str
    source: str
    image_url: Optional[str]
    scrape_result: str
    keyword_result: dict
    description: str
    created_at: datetime = datetime.utcnow()
