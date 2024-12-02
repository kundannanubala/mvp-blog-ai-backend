import re
from bs4 import BeautifulSoup
from typing import Optional

class HTMLCleaner:
    def __init__(self):
        # Compile regex patterns once for efficiency
        self.html_tag_pattern = re.compile('<.*?>')
        self.whitespace_pattern = re.compile(r'\s+')
        self.unwanted_phrases = [
            'Click here',
            'Read more',
            'Subscribe now',
            'Advertisement',
            'Share this',
            'Follow us',
            'Sign up',
            'Download now',
        ]

    async def clean_html_content(self, content: str) -> Optional[str]:
        """
        Clean HTML content using BeautifulSoup and regex.
        
        Args:
            content (str): Raw HTML content to clean
            
        Returns:
            str: Cleaned text content or None if cleaning fails
        """
        if not content:
            return None
            
        try:
            # First pass: Use BeautifulSoup for structured cleaning
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'iframe', 'noscript']):
                element.decompose()
                
            # Extract text content
            text = soup.get_text()
            
            # Second pass: Use regex for remaining cleanup
            text = self.html_tag_pattern.sub('', text)
            
            # Normalize whitespace
            text = self.whitespace_pattern.sub(' ', text)
            
            # Remove unwanted phrases
            for phrase in self.unwanted_phrases:
                text = text.replace(phrase, '')
            
            # Final cleanup
            text = text.strip()
            
            return text if text else None
            
        except Exception as e:
            print(f"Error cleaning HTML content: {str(e)}")
            return None
            
    async def clean_meta_description(self, description: str) -> Optional[str]:
        """
        Clean meta descriptions with special handling for SEO content.
        
        Args:
            description (str): Meta description to clean
            
        Returns:
            str: Cleaned meta description or None if cleaning fails
        """
        if not description:
            return None
            
        try:
            # Remove HTML entities
            text = BeautifulSoup(description, 'html.parser').get_text()
            
            # Remove URLs
            url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            text = url_pattern.sub('', text)
            
            # Normalize whitespace
            text = self.whitespace_pattern.sub(' ', text)
            
            # Remove unwanted phrases
            for phrase in self.unwanted_phrases:
                text = text.replace(phrase, '')
            
            return text.strip() if text.strip() else None
            
        except Exception as e:
            print(f"Error cleaning meta description: {str(e)}")
            return None

    async def clean_blog_content(self, content: str) -> Optional[str]:
        """
        Clean blog content while preserving important formatting.
        
        Args:
            content (str): Blog content to clean
            
        Returns:
            str: Cleaned blog content or None if cleaning fails
        """
        if not content:
            return None
            
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove unwanted elements but preserve paragraphs and headers
            for element in soup.find_all(['script', 'style', 'iframe', 'noscript', 'nav', 'footer', 'aside']):
                element.decompose()
            
            # Extract meaningful paragraphs and headers
            content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            # Build cleaned content
            cleaned_parts = []
            for element in content_elements:
                text = element.get_text().strip()
                if len(text) > 20:  # Only keep substantial paragraphs
                    cleaned_parts.append(text)
            
            return '\n\n'.join(cleaned_parts) if cleaned_parts else None
            
        except Exception as e:
            print(f"Error cleaning blog content: {str(e)}")
            return None 