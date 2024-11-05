import os
from groq import Groq

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
