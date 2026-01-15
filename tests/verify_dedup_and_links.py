import unittest
from services.news_fetcher import NewsFetcher
from unittest.mock import patch, MagicMock

class TestNewsFetcher(unittest.TestCase):
    def setUp(self):
        # Reset class level sets before each test
        NewsFetcher._seen_urls = set()
        NewsFetcher._seen_titles = set()
        self.fetcher = NewsFetcher()

    def test_exact_deduplication(self):
        url = "http://example.com/1"
        title = "Test Article 1"
        self.fetcher._register_article(title, url)
        
        # Test Duplicate URL
        self.assertTrue(self.fetcher._is_duplicate("Different Title", url))
        
        # Test Duplicate Title
        self.assertTrue(self.fetcher._is_duplicate(title, "http://different-url.com"))
        
        # Test Unique
        self.assertFalse(self.fetcher._is_duplicate("New Title", "http://new-url.com"))

    def test_fuzzy_deduplication(self):
        title1 = "Global Trade Slows Down Due to Tariffs"
        url1 = "http://example.com/trade1"
        self.fetcher._register_article(title1, url1)
        
        # Similar Title (High similarity)
        title2 = "Global Trade Slows Down Because of Tariffs" 
        self.assertTrue(self.fetcher._is_duplicate(title2, "http://example.com/trade2"))
        
        # Different Title
        title3 = "Tech Industry Booms in India"
        self.assertFalse(self.fetcher._is_duplicate(title3, "http://example.com/tech1"))

    @patch('requests.head')
    @patch('requests.get')
    def test_link_validation(self, mock_get, mock_head):
        # Case 1: Active Link (HEAD 200)
        mock_head.return_value.status_code = 200
        self.assertTrue(self.fetcher._is_link_valid("http://good-link.com"))
        
        # Case 2: Method Not Allowed (HEAD 405 -> GET 200)
        mock_head.return_value.status_code = 405
        mock_get.return_value.status_code = 200
        self.assertTrue(self.fetcher._is_link_valid("http://semi-good-link.com"))

        # Case 3: Dead Link (HEAD 404)
        mock_head.return_value.status_code = 404
        self.assertFalse(self.fetcher._is_link_valid("http://bad-link.com"))

if __name__ == '__main__':
    unittest.main()
