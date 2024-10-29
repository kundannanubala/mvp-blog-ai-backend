from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from models.articles import Article
from uuid import uuid4

async def save_processed_entries(processed_entries: list) -> list:
    """
    Save processed entries to the articles collection
    
    Args:
        processed_entries (list): List of processed entries from process_entry
        
    Returns:
        list: List of saved article IDs
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db['articles']
    
    saved_articles = []
    
    try:
        for entry in processed_entries:
            article = Article(
                id=str(uuid4()),
                **entry
            )
            
            # Check if article already exists
            existing_article = await collection.find_one({"link": article.link})
            if not existing_article:
                result = await collection.insert_one(article.dict())
                saved_articles.append(str(result.inserted_id))
                
    finally:
        client.close()
        
    return saved_articles
