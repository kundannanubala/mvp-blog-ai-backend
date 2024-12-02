from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime

class XmlUrl(BaseModel):
    """
    Data model for representing an XML URL.

    Attributes:
        id (str): A unique identifier for the XML URL, generated using the domain and a UUID.
        url (str): The URL of the XML feed.
        domain (str): The domain associated with the XML URL.
        created_at (datetime): The timestamp when the XML URL was created.
    """
    id: str
    url: str
    domain: str
    created_at: datetime

    def __init__(self, url: str, domain: str):
        """
        Initialize an XmlUrl instance.

        Args:
            url (str): The URL of the XML feed.
            domain (str): The domain associated with the XML URL.
        """
        super().__init__(
            id=self.generate_id(domain),  # Generate a unique ID using the domain
            url=url,
            domain=domain,
            created_at=datetime.now(),  # Set the creation timestamp to the current time
        )

    @staticmethod
    def generate_id(domain: str) -> str:
        """
        Generate a unique identifier for the XML URL.

        Args:
            domain (str): The domain associated with the XML URL.

        Returns:
            str: A unique identifier combining the domain and a UUID.
        """
        return f"{domain}_{uuid4()}"
