from pydantic import BaseModel, Field
from typing import List

class Keyword(BaseModel):
    keyword: str = Field(..., description="Single keyword")

class KeywordList(BaseModel):
    keywords: List[str] = Field(..., description="List of keywords")
