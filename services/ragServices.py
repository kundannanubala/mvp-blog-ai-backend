from astrapy import DataAPIClient
from datetime import datetime
import os
from core.config import settings
from astrapy.collection import Collection


async def store_article_in_vector_db(article_data: dict, username: str):
    # Retrieve environment variables
    token = settings.ASTRA_DB_APPLICATION_TOKEN
    api_endpoint = settings.ASTRA_DB_API_ENDPOINT
    collection_name = settings.COLLECTION_NAME

    # Connect to AstraDB
    client = DataAPIClient(token)
    database = client.get_database(api_endpoint)
    collection = database[collection_name]

    # Add metadata to the article data
    article_data['metadata'] = {
        'username': username,
        'created_at': datetime.utcnow().isoformat()
    }

    # Split scrape_result into chunks if it exceeds the size limit
    scrape_result = article_data.get('scrape_result', '')
    max_chunk_size = 4000  # Maximum allowed size
    if len(scrape_result) > max_chunk_size:
        chunks = [scrape_result[i:i + max_chunk_size] for i in range(0, len(scrape_result), max_chunk_size)]
        article_data['scrape_result_chunks'] = chunks
        del article_data['scrape_result']  # Remove the original large field
    else:
        article_data['scrape_result_chunks'] = [scrape_result]

    # Insert the article data into the collection
    try:
        result = collection.insert_one(article_data)
        return {"message": "Article stored successfully", "id": result.inserted_id}
    except Exception as e:
        return {"error": str(e)}

async def fetch_articles_by_username(username: str):
    # Retrieve environment variables
    token = settings.ASTRA_DB_APPLICATION_TOKEN
    api_endpoint = settings.ASTRA_DB_API_ENDPOINT
    collection_name = settings.COLLECTION_NAME

    # Connect to AstraDB
    client = DataAPIClient(token)
    database = client.get_database(api_endpoint)
    collection = database[collection_name]

    # Query the collection for documents with the specified username
    try:
        query = {"metadata.username": username}
        articles = collection.find(query)
        articles_list = list(articles)  # Convert the result to a list
        return articles_list
    except Exception as e:
        return {"error": str(e)}
