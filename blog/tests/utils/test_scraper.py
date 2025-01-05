import pytest
from bs4 import BeautifulSoup
import responses
import json
import time
from unittest.mock import patch, MagicMock, mock_open
from requests.exceptions import RequestException

# Import your WebScraper class
from blog.utils.scraper_utils import WebScraper  # Adjust import path as needed

@pytest.fixture
def scraper():
    """Fixture to create a WebScraper instance for testing."""
    return WebScraper('https://example.com')

@pytest.fixture
def mock_html():
    """Fixture providing sample HTML content."""
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1 class="product-title">Test Product</h1>
            <span class="price">$99.99</span>
            <div class="product-description">Product details here</div>
            <a class="next-page" href="/page/2">Next Page</a>
        </body>
    </html>
    """

class TestWebScraper:
    """Test suite for WebScraper class."""

    def test_initialization(self):
        """Test proper initialization of WebScraper instance."""
        scraper = WebScraper('https://example.com')
        
        assert scraper.base_url == 'https://example.com'
        assert 'User-Agent' in scraper.headers
        assert isinstance(scraper.headers['User-Agent'], str)

    def test_custom_headers(self):
        """Test initialization with custom headers."""
        custom_headers = {'User-Agent': 'CustomBot/1.0', 'Accept': 'text/html'}
        scraper = WebScraper('https://example.com', headers=custom_headers)
        
        assert scraper.headers == custom_headers
        assert scraper.session.headers['User-Agent'] == 'CustomBot/1.0'

    @responses.activate
    def test_get_soup_success(self, scraper, mock_html):
        """Test successful page fetching and parsing."""
        # Setup mock response
        responses.add(
            responses.GET,
            'https://example.com/test',
            body=mock_html,
            status=200
        )

        with patch('time.sleep'):  # Skip delay in tests
            soup = scraper.get_soup('https://example.com/test')
        
        assert isinstance(soup, BeautifulSoup)
        assert soup.select_one('h1.product-title').text == 'Test Product'

    @responses.activate
    def test_get_soup_failure(self, scraper):
        """Test handling of failed requests."""
        # Setup mock failed response
        responses.add(
            responses.GET,
            'https://example.com/error',
            status=404
        )

        with patch('time.sleep'):
            soup = scraper.get_soup('https://example.com/error')
        
        assert soup is None

    def test_extract_data(self, scraper, mock_html):
        """Test data extraction using selectors."""
        soup = BeautifulSoup(mock_html, 'html.parser')
        selectors = {
            'title': 'h1.product-title',
            'price': 'span.price',
            'description': 'div.product-description'
        }

        data = scraper.extract_data(soup, selectors)

        assert data['title'] == 'Test Product'
        assert data['price'] == '$99.99'
        assert data['description'] == 'Product details here'

    def test_extract_data_missing_elements(self, scraper):
        """Test handling of missing elements during extraction."""
        html = "<html><body><h1>Only Title</h1></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        selectors = {
            'title': 'h1',
            'missing': 'p.nonexistent'
        }

        data = scraper.extract_data(soup, selectors)

        assert data['title'] == 'Only Title'
        assert data['missing'] is None

    @responses.activate
    def test_scrape_pagination(self, scraper):
        """Test pagination scraping functionality."""
        # Setup mock responses for paginated pages
        pages = ['/page/1', '/page/2', '/page/3']
        
        for i, page in enumerate(pages):
            next_link = f'/page/{i+2}' if i < len(pages)-1 else ''
            html = f"""
            <html><body>
                <div>Page {i+1}</div>
                {'<a class="next-page" href="' + next_link + '">Next</a>' if next_link else ''}
            </body></html>
            """
            responses.add(
                responses.GET,
                f'https://example.com{page}',
                body=html,
                status=200
            )

        with patch('time.sleep'):  # Skip delay in tests
            visited_pages = scraper.scrape_pagination(
                'https://example.com/page/1',
                'a.next-page',
                max_pages=3
            )
        
        # Assert all pages were visited
        assert len(visited_pages) == 3
        assert visited_pages == [
            'https://example.com/page/1',
            'https://example.com/page/2',
            'https://example.com/page/3'
        ]


    def test_save_to_file(self, scraper):
        """Test data saving functionality."""
        test_data = [{'title': 'Test', 'price': '$99.99'}]
        mock_file = mock_open()

        with patch('builtins.open', mock_file):
            scraper.save_to_file(test_data, 'test.json')

        mock_file.assert_called_once_with('test.json', 'w', encoding='utf-8')
        handle = mock_file()
        
        # Verify JSON was written correctly
        written_data = json.loads(''.join(c[0][0] for c in handle.write.call_args_list))
        assert written_data == test_data

    @responses.activate
    def test_rate_limiting(self, scraper, mock_html):
        """Test rate limiting behavior."""
        responses.add(
            responses.GET,
            'https://example.com/test',
            body=mock_html,
            status=200
        )

        start_time = time.time()
        with patch('random.uniform', return_value=0.2):  # Fix random delay
            scraper.get_soup('https://example.com/test', delay=1.0)
        
        # Should have waited at least 1.2 seconds (base delay + fixed "random" delay)
        assert time.time() - start_time >= 1.2

    @pytest.mark.parametrize("error_code", [403, 500, 503])
    @responses.activate
    def test_different_error_responses(self, scraper, error_code):
        """Test handling of various HTTP error codes."""
        responses.add(
            responses.GET,
            f'https://example.com/error{error_code}',
            status=error_code
        )

        with patch('time.sleep'):
            soup = scraper.get_soup(f'https://example.com/error{error_code}')
        
        assert soup is None

    def test_network_timeout(self, scraper):
        """Test handling of network timeouts."""
        with patch('requests.Session.get', side_effect=RequestException("Timeout")):
            with patch('time.sleep'):
                soup = scraper.get_soup('https://example.com/timeout')
        
        assert soup is None

if __name__ == '__main__':
    pytest.main([__file__])