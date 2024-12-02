import os
from datetime import datetime
import vertexai
from vertexai.vision_models import ImageGenerationModel


async def generate_image_vertexai(summary_result: str) -> str:
    """
    Generate an image based on the provided summary content using Vertex AI.

    This function initializes the Vertex AI environment and uses a pre-trained image generation model
    to create an image that visually represents the given summary content. The generated image is saved
    locally, and the function returns the path to the saved image file.

    Args:
        summary_result (str): A string containing the summary content to base the image generation on.

    Returns:
        str: The file path to the locally saved image. Returns an empty string if image generation fails.
    """
    try:
        # Initialize Vertex AI with the specified project and location
        vertexai.init(
            project="researchdevelopment-424002",
            location="us-central1"
        )
        # Load the pre-trained image generation model
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

        # Create a prompt using the first 500 characters of the summary content
        context = summary_result[:500]
        prompt = f"""
        Create a professional image based on this content: {context}

        Consider the following guidelines:
        1. The image should be visually appealing and relevant to the content.
        2. Use a modern and professional art style.
        3. Ensure the image is suitable for a professional audience.
        4. Create a balanced composition.
        5. Use appropriate lighting and colors.
        """

        # Generate the image using the model with specified parameters
        images = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            language="en",
            aspect_ratio="16:9",  # Use widescreen ratio for blog images
            safety_filter_level="block_some",
            person_generation="allow_all",
        )

        if images:
            # Define the output directory and create it if it doesn't exist
            output_folder = "generated_blog_images"
            os.makedirs(output_folder, exist_ok=True)

            # Generate a unique filename using the current timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(
                output_folder, f"blog_image_{timestamp}.png"
            )

            # Save the generated image locally
            images[0].save(
                location=output_file,
                include_generation_parameters=False
            )

            print(f"Generated and saved image to: {output_file}")
            return output_file

        # Return an empty string if no image was generated
        return ""

    except Exception as e:
        # Log the error and return an empty string on failure
        print(f"Error generating image: {str(e)}")
        return ""
