import os
from datetime import datetime
import vertexai
from vertexai.vision_models import ImageGenerationModel
from core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_image_vertexai(summary_result: str) -> str:
    """Generate image with enhanced validation and error handling."""
    try:
        # Input validation
        if not summary_result or len(summary_result.strip()) < 50:
            logger.error("Error: Insufficient content for image generation")
            return ""

        # Initialize Vertex AI
        vertexai.init(project=settings.GOOGLE_CLOUD_PROJECT, location="us-central1")
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

        # Create context-aware prompt
        context = summary_result[:500].replace('\n', ' ').strip()
        prompt = f"""
        Create a professional blog header image based on this content:
        {context}

        Requirements:
        - Professional and modern style
        - Clean composition
        - Suitable for business audience
        - High contrast for readability
        - Balanced visual elements
        """

        # Generate image with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting image generation (attempt {attempt + 1}/{max_retries})")
                images = model.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    language="en",
                    aspect_ratio="16:9",
                    safety_filter_level="block_some",
                    person_generation="allow_all",
                )

                if not images:
                    if attempt == max_retries - 1:
                        logger.error("Error: No images generated after all attempts")
                        return ""
                    logger.warning(f"No images generated on attempt {attempt + 1}, retrying...")
                    continue

                # Save image
                output_folder = "generated_blog_images"
                os.makedirs(output_folder, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = os.path.join(output_folder, f"blog_image_{timestamp}.png")
                
                images[0].save(location=output_file, include_generation_parameters=False)
                logger.info(f"Successfully generated image: {output_file}")
                return output_file

            except Exception as retry_error:
                logger.error(f"Attempt {attempt + 1} failed: {str(retry_error)}")
                if attempt == max_retries - 1:
                    raise

    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        return ""
