import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from services.xmlServices import (
    scraper,
    summary,
    image,
    blog,
    keyword,
    process_entry,
    get_consolidated_todays_feeds,
    get_consolidated_feeds,
    get_xml_urls_from_db
)
from bs4 import BeautifulSoup
import feedparser

# Fixtures
@pytest.fixture
def mock_feed_entry():
    return Mock(
        title="Test Article",
        link="https://test.com/article",
        published="Mon, 01 Jan 2024 12:00:00 GMT",
        published_parsed=(2024, 1, 1, 12, 0, 0, 0, 1, 0),
        media_content=[{'url': 'https://test.com/image.jpg'}]
    )

@pytest.fixture
def mock_html_content():
    return """
    <html>
        <body>
            <article>
                <h1>Test Article</h1>
                <p>This is a test paragraph with more than 20 characters.</p>
                <p>This is another meaningful paragraph for testing purposes.</p>
                <script>Some script to be removed</script>
                <div class="advertisement">Ad content to remove</div>
            </article>
        </body>
    </html>
    """

@pytest.fixture
def mock_mongodb_client():
    async def mock_find_one(*args, **kwargs):
        return None

    client = AsyncMock()
    db = AsyncMock()
    collection = AsyncMock()
    collection.find_one = mock_find_one
    collection.insert_one = AsyncMock()
    db.__getitem__.return_value = collection
    client.__getitem__.return_value = db
    return client

# Tests for scraper function
@pytest.mark.asyncio
async def test_scraper_success(mock_html_content, mock_mongodb_client):
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html_content)
        
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_session.return_value.get.return_value = mock_context

        with patch('motor.motor_asyncio.AsyncIOMotorClient', return_value=mock_mongodb_client):
            result = await scraper("https://test.com/article")
            
            assert "This is a test paragraph" in result
            assert "This is another meaningful paragraph" in result
            assert "Some script to be removed" not in result
            assert "Ad content to remove" not in result

@pytest.mark.asyncio
async def test_scraper_cached_content(mock_mongodb_client):
    cached_content = "This is cached content"
    mock_mongodb_client['test_db']['scraped_content'].find_one = AsyncMock(
        return_value={"content": cached_content}
    )

    with patch('motor.motor_asyncio.AsyncIOMotorClient', return_value=mock_mongodb_client):
        result = await scraper("https://test.com/article")
        assert result == cached_content

# Tests for summary function
@pytest.mark.asyncio
async def test_summary_success():
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="Test summary content"))
    ]

    with patch('groq.AsyncGroq.chat.completions.create', 
               new_callable=AsyncMock, 
               return_value=mock_response):
        result = await summary("Test content to summarize")
        assert result == "Test summary content"

@pytest.mark.asyncio
async def test_summary_error():
    with patch('groq.AsyncGroq.chat.completions.create', 
               side_effect=Exception("API Error")):
        result = await summary("Test content")
        assert "Error generating summary" in result

# Tests for process_entry
@pytest.mark.asyncio
async def test_process_entry(mock_feed_entry):
    with patch('services.xmlServices.scraper', 
              new_callable=AsyncMock, 
              return_value="Scraped content"):
        with patch('services.xmlServices.summary', 
                  new_callable=AsyncMock, 
                  return_value="Summary content"):
            result = await process_entry(mock_feed_entry, "https://test.com/feed")
            
            assert result['title'] == "Test Article"
            assert result['link'] == "https://test.com/article"
            assert result['source'] == "https://test.com/feed"
            assert result['image_url'] == "https://test.com/image.jpg"
            assert result['scrape_result'] == "Scraped content"
            assert result['summary_result'] == "Summary content"

# Tests for consolidated feeds
@pytest.mark.asyncio
async def test_get_consolidated_todays_feeds():
    mock_urls = ["https://test.com/feed1", "https://test.com/feed2"]
    mock_feed = Mock(entries=[Mock(
        title="Today's Article",
        link="https://test.com/article",
        published="Mon, 01 Jan 2024 12:00:00 GMT",
        published_parsed=(datetime.now().year, 
                        datetime.now().month, 
                        datetime.now().day, 
                        12, 0, 0, 0, 1, 0)
    )])

    with patch('feedparser.parse', return_value=mock_feed):
        with patch('services.xmlServices.process_entry', 
                  new_callable=AsyncMock, 
                  return_value={"title": "Today's Article"}):
            with patch('services.articleServices.save_processed_entries', 
                      new_callable=AsyncMock, 
                      return_value=True):
                result = await get_consolidated_todays_feeds(mock_urls)
                assert len(result) > 0
                assert result[0]["title"] == "Today's Article"

# Tests for XML URLs from DB
@pytest.mark.asyncio
async def test_get_xml_urls_from_db(mock_mongodb_client):
    expected_urls = [
        {"url": "https://test.com/feed1"},
        {"url": "https://test.com/feed2"}
    ]
    
    mock_cursor = AsyncMock()
    mock_cursor.to_list = AsyncMock(return_value=expected_urls)
    mock_mongodb_client['test_db']['xml_urls'].find = Mock(return_value=mock_cursor)

    with patch('motor.motor_asyncio.AsyncIOMotorClient', return_value=mock_mongodb_client):
        result = await get_xml_urls_from_db()
        assert result == expected_urls

# Helper function tests
@pytest.mark.asyncio
async def test_image():
    result = await image("Test content")
    assert "Image extracted from" in result

@pytest.mark.asyncio
async def test_blog():
    result = await blog("Test content")
    assert "Blog content from" in result

@pytest.mark.asyncio
async def test_keyword():
    result = await keyword("Test content")
    assert "Keywords extracted from" in result 