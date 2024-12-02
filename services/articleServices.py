from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from models.articles import Article
from uuid import uuid4
from services.summaryServices import summary


async def save_processed_entries(processed_entries: list) -> list:
    """
    Save processed entries to the articles collection in the database.

    This function processes each entry by generating a summary and then saves it to the database
    if it doesn't already exist. It returns a list of IDs of the saved articles.

    Args:
        processed_entries (list): A list of dictionaries, each representing a processed article entry.

    Returns:
        list: A list of IDs of the articles that were successfully saved to the database.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db["articles"]

    saved_articles = []

    try:
        for entry in processed_entries:
            # Skip entries without a scrape result
            if not entry.get("scrape_result"):
                continue

            try:
                # Generate a summary for the article's scrape result
                summary_text = await summary(entry["scrape_result"])
                if summary_text:
                    entry["summary"] = summary_text
                else:
                    print(
                        f"Warning: Could not generate summary for article: {entry.get('title', 'Unknown')}"
                    )
                    entry["summary"] = "Summary not available"

                # Create an Article object with a unique ID
                article = Article(ID=uuid4().hex, **entry)

                # Check if the article already exists in the database
                existing_article = await collection.find_one({"link": article.link})
                if not existing_article:
                    # Insert the new article into the collection
                    result = await collection.insert_one(article.dict())
                    saved_articles.append(str(result.inserted_id))
                    print(
                        f"Saved article with summary: {summary_text[:100]}..."
                    )  # Log the saved article

            except Exception as e:
                print(
                    f"Error processing entry {entry.get('title', 'Unknown')}: {str(e)}"
                )
                continue

    finally:
        # Ensure the database client is closed after operations
        client.close()

    return saved_articles


async def get_article():
    """
    Retrieve all articles from the database.

    This function fetches all articles from the 'articles' collection and converts their ObjectId
    to a string format for easier handling.

    Returns:
        list: A list of articles with their ObjectId converted to a string.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db["articles"]

    articles = await collection.find().to_list(length=None)

    # Convert ObjectId to string for each article
    for article in articles:
        article["id"] = str(article["_id"])  # Convert ObjectId to string
        del article["_id"]  # Remove the original ObjectId field

    client.close()
    return articles


async def get_articles_by_ids(article_ids: list) -> list:
    """
    Fetch articles with specified IDs and return their scrape results.

    This function retrieves articles from the database that match the given list of IDs
    and returns their scrape results.

    Args:
        article_ids (list): A list of article IDs to fetch from the database.

    Returns:
        list: A list of scrape results from the specified articles.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db["articles"]

    try:
        # Find articles with IDs in the provided list
        articles = await collection.find({"ID": {"$in": article_ids}}).to_list(
            length=None
        )
        # Extract and return the scrape results of the found articles
        return [
            article.get("scrape_result", "")
            for article in articles
            if article.get("scrape_result")
        ]
    finally:
        # Ensure the database client is closed after operations
        client.close()
