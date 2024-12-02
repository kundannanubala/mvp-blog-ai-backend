from pydantic import BaseModel, Field
from typing import List

class Keyword(BaseModel):
    """
    Data model for representing a single keyword.

    Attributes:
        keyword (str): A single keyword.
    """
    keyword: str = Field(..., description="A single keyword")

class KeywordList(BaseModel):
    """
    Data model for representing a list of keywords.

    Attributes:
        keywords (List[str]): A list containing multiple keywords.
    """
    keywords: List[str] = Field(..., description="A list of keywords")
