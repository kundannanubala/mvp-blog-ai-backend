import os
import google.generativeai as genai
async def summary(scrape_result: str) -> str:
    """
    Summarizes the scraped content using Groq's Mixtral model.
    Returns a concise summary while preserving key context.
    """
    # try:
    #     # Add exponential backoff retry logic
    #     max_retries = 3
    #     base_delay = 5  # seconds
        
    #     for attempt in range(max_retries):
    #         try:
    #             prompt = f"""Summarize the following text in approximately 100 words while preserving all key context and main points:

    #             {scrape_result}"""

    #             response = await client.chat.completions.create(
    #                 messages=[{"role": "user", "content": prompt}],
    #                 model="llama-3.1-70b-versatile",
    #                 temperature=0.5,
    #                 max_tokens=8000,
    #                 top_p=1,
    #             )
                
    #             if response.choices[0].message.content:
    #                 return response.choices[0].message.content.strip()
                    
    #         except Exception as e:
    #             if "rate_limit_exceeded" in str(e):
    #                 if attempt < max_retries - 1:
    #                     delay = base_delay * (2 ** attempt)  # Exponential backoff
    #                     await asyncio.sleep(delay)
    #                     continue
    #             raise e
                
    #     return "No summary generated"

    # except Exception as e:
    #     return f"Error generating summary: {str(e)}"
    try:
        import google.generativeai as genai
        
        # Configure Gemini API
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        
        # Initialize Gemini 1.5 Flash model
        model = genai.GenerativeModel("gemini-1.5-flash-8b")
        
        # Create prompt for summarization
        prompt = f"""Summarize the following text in approximately 100 words while preserving all key context and main points:

        {scrape_result}"""
        
        # Generate summary
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text.strip()
            
        return "No summary generated"
        
    except Exception as e:
        return f"Error generating summary: {str(e)}"