from pydantic import BaseModel
from typing import List, Optional

class UserPersona(BaseModel):
    """
    Data model representing a user's persona for content generation.

    Attributes:
        writing_style (str): The preferred writing style of the user.
        tone (str): The tone the user prefers in their content.
        expertise_level (str): The level of expertise the user wants to convey.
        target_audience (str): The intended audience for the user's content.
        preferred_content_types (List[str]): Types of content the user prefers.
        industry_focus (List[str]): Industries the user is focused on.
        content_length_preference (str): Preferred length of the content.
        key_interests (List[str]): Key interests of the user.
        language_style (str): The language style the user prefers.
        formatting_preferences (Optional[dict]): Any specific formatting preferences the user has.
    """
    writing_style: str
    tone: str
    expertise_level: str
    target_audience: str
    preferred_content_types: List[str]
    industry_focus: List[str]
    content_length_preference: str
    key_interests: List[str]
    language_style: str
    formatting_preferences: Optional[dict] = {}