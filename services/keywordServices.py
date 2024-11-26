import os
from groq import Groq
from collections import Counter
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

async def keyword_generation(scrape_result: str) -> str:
    """
    Extract relevant keywords from the blog content using Groq API.
    Uses the scrape result and metadata to generate keywords with maximum relevance.
    """

    # Initialize Groq client
    client = Groq()

    # Create prompt for keyword extraction
    prompt = f"""
    Please analyze this blog content and extract the most relevant keywords.
    Focus on technical terms, key concepts, and important topics.
    Format the output as a comma-separated list of keywords.
    
    Content to analyze:
    {scrape_result}
    """

    # Call Groq API for keyword extraction
    completion = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {
                "role": "system", 
                "content": "You are a keyword extraction specialist. Extract relevant keywords from content."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=256,
        top_p=1,
        stream=False
    )

    # Get keywords from response
    keywords = completion.choices[0].message.content.strip()
    
    return keywords

async def extract_matching_keywords(scrape_result: str) -> dict:
    """
    Extract and count keywords in the scrape result that match the user's keywords.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    keywords_collection = db['keywords']
    
    # Get all keywords from the collection
    keywords_cursor = keywords_collection.find({})
    keywords_list = await keywords_cursor.to_list(length=None)
    user_keywords = [doc["keywords"] for doc in keywords_list]  # Changed from "keyword" to "keywords"
    # Flatten the list since keywords might be stored as lists
    user_keywords = [item for sublist in user_keywords for item in sublist]
    print("User keywords:", user_keywords)

    # Convert scrape result to lowercase for case-insensitive matching
    scrape_result = scrape_result.lower()
    
    # Initialize empty dictionary for results
    keyword_counts = {}
    
    # Count occurrences for each keyword
    for keyword in user_keywords:
        keyword_lower = keyword.lower()
        count = scrape_result.count(keyword_lower)
        if count > 0:
            keyword_counts[keyword] = count
    
    print(f"Keywords found: {keyword_counts}")
    return keyword_counts

