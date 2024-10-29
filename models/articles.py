from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Article(BaseModel):
    id: str
    title: str
    published: str
    link: str
    source: str
    image_url: Optional[str]
    scrape_result: str
    summary_result: str
    image_result: str
    blog_result: str
    keyword_result: str
    created_at: datetime = datetime.utcnow()
