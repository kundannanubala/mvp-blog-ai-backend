import os
from groq import Groq
from collections import Counter
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings


async def keyword_generation(scrape_result: str) -> str:
    """
    Extract relevant keywords from the provided blog content using the Groq API.

    This function utilizes the Groq API to analyze the given scrape result and extract
    the most relevant keywords. The focus is on identifying technical terms, key concepts,
    and important topics. The output is formatted as a comma-separated list of keywords.

    Args:
        scrape_result (str): The content of the blog post to analyze for keyword extraction.

    Returns:
        str: A comma-separated string of extracted keywords.
    """

    # Initialize the Groq client for API interaction
    client = Groq()

    # Construct the prompt for the Groq API to perform keyword extraction
    prompt = f"""
    Please analyze this blog content and extract the most relevant keywords.
    Focus on technical terms, key concepts, and important topics.
    Format the output as a comma-separated list of keywords.

    Content to analyze:
    {scrape_result}
    """

    # Call the Groq API to generate keywords based on the provided content
    completion = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {
                "role": "system",
                "content": "You are a keyword extraction specialist. Extract relevant keywords from content.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=256,
        top_p=1,
        stream=False,
    )

    # Extract and return the keywords from the API response
    keywords = completion.choices[0].message.content.strip()
    return keywords


async def extract_matching_keywords(scrape_result: str) -> dict:
    """
    Extract and count the occurrences of keywords in the scrape result that match the user's stored keywords.

    This function retrieves user-defined keywords from a MongoDB collection and counts their occurrences
    in the provided scrape result. The matching is case-insensitive.

    Args:
        scrape_result (str): The content to analyze for matching keywords.

    Returns:
        dict: A dictionary with keywords as keys and their respective counts as values.
    """

    # Initialize the MongoDB client and access the keywords collection
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    keywords_collection = db["keywords"]

    # Retrieve all keywords from the database collection
    keywords_cursor = keywords_collection.find({})
    keywords_list = await keywords_cursor.to_list(length=None)

    # Extract and flatten the list of user keywords
    user_keywords = [doc["keywords"] for doc in keywords_list]
    user_keywords = [item for sublist in user_keywords for item in sublist]
    print("User keywords:", user_keywords)

    # Convert the scrape result to lowercase for case-insensitive keyword matching
    scrape_result = scrape_result.lower()

    # Initialize a dictionary to store the count of each keyword found
    keyword_counts = {}

    # Count the occurrences of each user keyword in the scrape result
    for keyword in user_keywords:
        keyword_lower = keyword.lower()
        count = scrape_result.count(keyword_lower)
        if count > 0:
            keyword_counts[keyword] = count

    print(f"Keywords found: {keyword_counts}")
    return keyword_counts
