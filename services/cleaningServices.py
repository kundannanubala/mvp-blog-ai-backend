import re
from bs4 import BeautifulSoup
from typing import Optional

class HTMLCleaner:
    def __init__(self):
        """
        Initialize the HTMLCleaner with precompiled regex patterns and a list of unwanted phrases.
        
        Attributes:
            html_tag_pattern (Pattern): Compiled regex pattern to match HTML tags.
            whitespace_pattern (Pattern): Compiled regex pattern to match whitespace.
            unwanted_phrases (List[str]): List of phrases to be removed from the content.
        """
        # Compile regex patterns once for efficiency
        self.html_tag_pattern = re.compile("<.*?>")
        self.whitespace_pattern = re.compile(r"\s+")
        self.unwanted_phrases = [
            "Click here",
            "Subscribe now",
            "Advertisement",
            "Share this",
            "Follow us",
            "Sign up",
            "Download now",
        ]

    async def clean_html_content(self, content: str) -> Optional[str]:
        """
        Clean HTML content by removing unwanted HTML tags, normalizing whitespace, and eliminating specific phrases.

        Args:
            content (str): Raw HTML content to clean.

        Returns:
            Optional[str]: Cleaned text content or None if cleaning fails or content is empty.
        """
        if not content:
            return None

        try:
            # Use BeautifulSoup to parse and clean the HTML content
            soup = BeautifulSoup(content, "html.parser")

            # Remove unwanted HTML elements such as scripts and styles
            for element in soup.find_all(["script", "style", "iframe", "noscript"]):
                element.decompose()

            # Extract text content from the cleaned HTML
            text = soup.get_text()

            # Remove any remaining HTML tags using regex
            text = self.html_tag_pattern.sub("", text)

            # Normalize whitespace to a single space
            text = self.whitespace_pattern.sub(" ", text)

            # Remove predefined unwanted phrases from the text
            for phrase in self.unwanted_phrases:
                text = text.replace(phrase, "")

            # Trim leading and trailing whitespace
            text = text.strip()

            return text if text else None

        except Exception as e:
            print(f"Error cleaning HTML content: {str(e)}")
            return None

    async def clean_meta_description(self, description: str) -> Optional[str]:
        """
        Clean meta descriptions by removing HTML entities, URLs, and unwanted phrases.

        Args:
            description (str): Meta description to clean.

        Returns:
            Optional[str]: Cleaned meta description or None if cleaning fails or description is empty.
        """
        if not description:
            return None

        try:
            # Remove HTML entities using BeautifulSoup
            text = BeautifulSoup(description, "html.parser").get_text()

            # Define a regex pattern to match URLs
            url_pattern = re.compile(
                r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
            )
            # Remove URLs from the text
            text = url_pattern.sub("", text)

            # Normalize whitespace to a single space
            text = self.whitespace_pattern.sub(" ", text)

            # Remove predefined unwanted phrases from the text
            for phrase in self.unwanted_phrases:
                text = text.replace(phrase, "")

            # Trim leading and trailing whitespace
            return text.strip() if text.strip() else None

        except Exception as e:
            print(f"Error cleaning meta description: {str(e)}")
            return None

    async def clean_blog_content(self, content: str) -> Optional[str]:
        """
        Clean blog content while preserving important formatting such as paragraphs and headers.

        Args:
            content (str): Blog content to clean.

        Returns:
            Optional[str]: Cleaned blog content or None if cleaning fails or content is empty.
        """
        if not content:
            return None

        try:
            # Use BeautifulSoup to parse the blog content
            soup = BeautifulSoup(content, "html.parser")

            # Remove unwanted elements but preserve paragraphs and headers
            for element in soup.find_all(
                ["script", "style", "iframe", "noscript", "nav", "footer", "aside"]
            ):
                element.decompose()

            # Extract meaningful paragraphs and headers
            content_elements = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"])

            # Collect cleaned content parts
            cleaned_parts = []
            for element in content_elements:
                text = element.get_text().strip()
                if len(text) > 20:  # Only keep substantial paragraphs
                    cleaned_parts.append(text)

            # Join the cleaned parts with double newlines to preserve paragraph breaks
            return "\n\n".join(cleaned_parts) if cleaned_parts else None

        except Exception as e:
            print(f"Error cleaning blog content: {str(e)}")
            return None
