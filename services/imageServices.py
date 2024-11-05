import os
from datetime import datetime
import vertexai
from vertexai.vision_models import ImageGenerationModel

async def generate_image_vertexai(summary_result: str) -> str:
    """
    Generates an image based on the scraped content using Vertex AI.
    Returns the path to the locally saved image.
    """
    try:
        # Initialize Vertex AI
        vertexai.init(project="researchdevelopment-424002", location="us-central1")
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

        # Create a prompt based on the scraped content
        # Use first 500 characters of scrape_result to create context
        context = summary_result[:500]
        
        prompt = f"""
        Create a professional image based on this content: {context}
        
        Consider the following guidelines:
        1. The image should be visually appealing and relevant to the content
        2. Use a modern and professional art style
        3. Ensure the image is suitable for a professional audience
        4. Create a balanced composition
        5. Use appropriate lighting and colors
        """

        # Generate the image
        images = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            language="en",
            aspect_ratio="16:9",  # Using widescreen ratio for blog images
            safety_filter_level="block_some",
            person_generation="allow_all",
        )

        if images:
            # Create output directory if it doesn't exist
            output_folder = "generated_blog_images"
            os.makedirs(output_folder, exist_ok=True)

            # Generate unique filename using timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_folder, f"blog_image_{timestamp}.png")

            # Save the image locally
            images[0].save(location=output_file, include_generation_parameters=False)
            
            print(f"Generated and saved image to: {output_file}")
            return output_file

        return ""  # Return empty string if no image was generated

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return ""  # Return empty string on error
