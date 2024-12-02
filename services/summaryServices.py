import os
import google.generativeai as genai
from core.config import settings
import asyncio
from typing import Optional

async def summary(scrape_result: str) -> Optional[str]:
    """
    Generate a concise summary of the provided scraped content using Google's Gemini model.

    This function utilizes the Gemini model to produce a summary that captures the key points
    and maintains factual accuracy. The input text is truncated if it exceeds the model's context limit.

    Args:
        scrape_result (str): The text content obtained from web scraping that needs summarization.

    Returns:
        Optional[str]: A string containing the summarized text, or None if the summarization fails.
    """
    try:
        # Configure the Gemini API with the provided API key from settings
        genai.configure(api_key=settings.GOOGLE_API_KEY)

        # Initialize the Gemini model with the specified version for generating summaries
        model = genai.GenerativeModel("gemini-1.5-flash-8b")  # Flash model is chosen for enhanced summary quality

        # Define the maximum number of characters allowed by the Gemini model's context
        max_chars = 30000
        # Truncate the input text to fit within the model's context limit
        truncated_text = (
            scrape_result[:max_chars]
            if len(scrape_result) > max_chars
            else scrape_result
        )

        # Construct the prompt for the Gemini model to generate a summary
        prompt = f"""Summarize the following text in approximately 100 words.
        Focus on key points and maintain factual accuracy:

        {truncated_text}"""

        # Attempt to generate the summary with a maximum of 3 retries in case of failure
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use asyncio to run the model's content generation in a separate thread
                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                    generation_config={
                        "temperature": 0.3,  # Controls randomness in the output
                        "top_p": 0.8,       # Nucleus sampling parameter
                        "top_k": 40,        # Limits the number of highest probability tokens considered
                    },
                )

                # If a valid response is received, return the stripped summary text
                if response.text:
                    return response.text.strip()

            except Exception as e:
                # If the last retry fails, raise the exception
                if attempt == max_retries - 1:
                    raise e
                # Implement exponential backoff before retrying
                await asyncio.sleep(2**attempt)

        # Return None if all attempts to generate a summary fail
        return None

    except Exception as e:
        # Log the error message if an exception occurs during the summarization process
        print(f"Error generating summary: {str(e)}")
        return None
