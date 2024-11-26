from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class Article(BaseModel):
    id: str
    title: str
    published: str
    link: str
    source: str
    image_url: Optional[str]
    scrape_result: str
    keyword_result: dict
    created_at: datetime = datetime.utcnow()
