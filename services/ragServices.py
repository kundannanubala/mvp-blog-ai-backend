from astrapy import DataAPIClient
from datetime import datetime
import os
from core.config import settings
from astrapy.collection import Collection

async def store_article_in_vector_db(article_data: dict):
    """
    Store an article in the vector database.

    This function connects to the AstraDB vector database and stores the provided article data.
    It adds metadata to the article and splits the 'scrape_result' into manageable chunks if it
    exceeds the maximum allowed size.

    Args:
        article_data (dict): A dictionary containing the article data to be stored.

    Returns:
        dict: A dictionary containing a success message and the inserted article ID, or an error message.
    """
    # Retrieve necessary environment variables for database connection
    token = settings.ASTRA_DB_APPLICATION_TOKEN
    api_endpoint = settings.ASTRA_DB_API_ENDPOINT
    collection_name = settings.COLLECTION_NAME

    # Establish a connection to AstraDB
    client = DataAPIClient(token)
    database = client.get_database(api_endpoint)
    collection = database[collection_name]

    # Add metadata with the current timestamp to the article data
    article_data["metadata"] = {"created_at": datetime.utcnow().isoformat()}

    # Handle large 'scrape_result' by splitting it into smaller chunks
    scrape_result = article_data.get("scrape_result", "")
    max_chunk_size = 4000  # Define the maximum allowed size for each chunk
    if len(scrape_result) > max_chunk_size:
        # Split the scrape_result into chunks of max_chunk_size
        chunks = [
            scrape_result[i: i + max_chunk_size]
            for i in range(0, len(scrape_result), max_chunk_size)
        ]
        article_data["scrape_result_chunks"] = chunks
        del article_data["scrape_result"]  # Remove the original large field to save space
    else:
        # If the scrape_result is within the size limit, store it as a single chunk
        article_data["scrape_result_chunks"] = [scrape_result]

    # Attempt to insert the article data into the database collection
    try:
        result = collection.insert_one(article_data)
        return {
            "message": "Article stored successfully",
            "id": result.inserted_id
        }
    except Exception as e:
        return {"error": str(e)}

async def fetch_articles_by_username(username: str):
    """
    Fetch articles from the vector database by username.

    This function queries the AstraDB vector database to retrieve all articles associated with
    the specified username.

    Args:
        username (str): The username to filter articles by.

    Returns:
        list: A list of articles associated with the given username, or an error message.
    """
    # Retrieve necessary environment variables for database connection
    token = settings.ASTRA_DB_APPLICATION_TOKEN
    api_endpoint = settings.ASTRA_DB_API_ENDPOINT
    collection_name = settings.COLLECTION_NAME

    # Establish a connection to AstraDB
    client = DataAPIClient(token)
    database = client.get_database(api_endpoint)
    collection = database[collection_name]

    # Query the collection for articles with the specified username in metadata
    try:
        query = {"metadata.username": username}
        articles = collection.find(query)
        articles_list = list(articles)  # Convert the query result to a list
        return articles_list
    except Exception as e:
        return {"error": str(e)}
