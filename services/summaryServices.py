import os
import google.generativeai as genai
from core.config import settings
import asyncio
from typing import Optional

async def summary(scrape_result: str) -> Optional[str]:
    """
    Summarizes the scraped content using Google's Gemini model.
    Returns a concise summary while preserving key context.
    """
    try:
        # Configure Gemini API
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Initialize Gemini model
        model = genai.GenerativeModel("gemini-1.5-flash-8b")  # Using Flash model for better summaries
        
        # Truncate input if too long (Gemini has a context limit)
        max_chars = 30000
        truncated_text = scrape_result[:max_chars] if len(scrape_result) > max_chars else scrape_result
        
        # Create prompt for summarization
        prompt = f"""Summarize the following text in approximately 100 words. 
        Focus on key points and maintain factual accuracy:

        {truncated_text}"""
        
        # Generate summary with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                    generation_config={
                        'temperature': 0.3,
                        'top_p': 0.8,
                        'top_k': 40,
                    }
                )
                
                if response.text:
                    return response.text.strip()
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        return None
        
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return None