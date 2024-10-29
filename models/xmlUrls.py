from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime

class XmlUrl(BaseModel):
    id: str
    url: str
    domain: str
    created_at: datetime

    def __init__(self, url: str, domain: str):
        super().__init__(id=self.generate_id(domain), url=url, domain=domain, created_at=datetime.now())

    @staticmethod
    def generate_id(domain: str) -> str:
        return f"{domain}_{uuid4()}"
