import os
import feedparser
import requests
from datetime import datetime, timedelta
import time
from urllib.parse import quote
import logging
import difflib

logger = logging.getLogger(__name__)

class NewsFetcher:
    # Class-level sets to persist across different tool instantiations
    _seen_urls = set()
    _seen_titles = set()

    def __init__(self):
        pass

    def _is_link_valid(self, url):
        """
        Verifies if the link is accessible (returns 200 OK).
        Uses a short timeout to avoid slowing down the process too much.
        """
        try:
            # We use a User-Agent to avoid being blocked by some servers that reject empty/bot UAs
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            # Try HEAD first as it's lighter
            response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            
            # Some servers might not support HEAD or return 405 Method Not Allowed, retry with GET
            if response.status_code == 405:
                response = requests.get(url, headers=headers, timeout=5, stream=True)
                
            if response.status_code == 200:
                return True
            else:
                logger.warning(f"Link valid check failed for {url}: Status {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"Link valid check error for {url}: {e}")
            return False

    def _is_duplicate(self, title, url):
        """
        Checks if the article is a duplicate based on URL or fuzzy title matching.
        """
        # 1. Check URL exact match
        if url in self._seen_urls:
            logger.info(f"Duplicate URL found: {url}")
            return True

        # 2. Check Title exact match
        if title in self._seen_titles:
            logger.info(f"Duplicate Title found: {title}")
            return True

        # 3. Fuzzy Title Match
        # Check against all seen titles for high similarity
        # This might be slow if _seen_titles grows very large, but for a daily run it's fine.
        for seen_title in self._seen_titles:
            similarity = difflib.SequenceMatcher(None, title.lower(), seen_title.lower()).ratio()
            if similarity > 0.85: # 85% similarity threshold
                logger.info(f"Fuzzy duplicate found: '{title}' is similar to '{seen_title}' ({similarity:.2f})")
                return True

        return False

    def _register_article(self, title, url):
        """
        Registers the article in the seen sets.
        """
        self._seen_urls.add(url)
        self._seen_titles.add(title)

    def fetch_news(self, topic, lookback_hours=48):
        """
        Fetches news for a given topic using Google News RSS.
        """
        encoded_topic = quote(topic)
        rss_url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-US&gl=US&ceid=US:en"
        
        logger.info(f"Fetching news for topic: {topic} from {rss_url}")
        
        feed = feedparser.parse(rss_url)
        
        articles = []
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)

        if not feed.entries:
            logger.warning(f"No entries found for topic: {topic}")
            return []

        for entry in feed.entries:
            title = entry.title
            url = entry.link
            
            # Deduplication
            if self._is_duplicate(title, url):
                continue
            
            # Time filtering
            published_parsed = entry.get('published_parsed')
            if published_parsed:
                published_dt = datetime.fromtimestamp(time.mktime(published_parsed))
                if published_dt < cutoff_time:
                    continue
            
            # Link Validation
            # NOTE: Doing this sequentially for every potential article can be slow.
            # We might want to only validate the ones we are about to keep?
            # Current logic: Validate before adding.
            if not self._is_link_valid(url):
                continue

            # If all checks pass, register and add
            self._register_article(title, url)
            
            articles.append({
                "title": title,
                "url": url,
                "source": entry.source.title if hasattr(entry, 'source') else "Unknown",
                "date": entry.published,
                "content": entry.summary if hasattr(entry, 'summary') else title
            })
            
            # Limit to top 10 per topic
            if len(articles) >= 10:
                break
                
        logger.info(f"Found {len(articles)} unique & valid articles for {topic}")
        return articles

    def fetch_news_gnews(self, topic, lookback_hours=48):
        """
        Fetches news for a given topic using GNews API.
        """
        api_key = os.getenv("GNEWS_API_KEY")
        if not api_key:
            logger.error("GNEWS_API_KEY not found in environment variables.")
            return []

        url = "https://gnews.io/api/v4/search"
        from_time = (datetime.utcnow() - timedelta(hours=lookback_hours)).strftime("%Y-%m-%dT%H:%M:%SZ")

        params = {
            "q": topic,
            "lang": "en",
            "country": "us",
            "max": 10,
            "apikey": api_key,
            "from": from_time,
            "sortby": "publishedAt"
        }

        logger.info(f"Fetching news for topic: {topic} from GNews API")
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            if "articles" not in data:
                logger.warning(f"No articles key in GNews response for {topic}")
                return []

            for entry in data["articles"]:
                title = entry["title"]
                url = entry["url"]

                # Deduplication
                if self._is_duplicate(title, url):
                    continue

                # Link Validation
                if not self._is_link_valid(url):
                    continue
                
                # Register
                self._register_article(title, url)
                
                articles.append({
                    "title": title,
                    "url": url,
                    "source": entry["source"]["name"],
                    "date": entry["publishedAt"],
                    "content": entry["description"]
                })
            
            logger.info(f"Found {len(articles)} unique & valid articles for {topic} via GNews")
            return articles

        except Exception as e:
            logger.error(f"Failed to fetch from GNews for {topic}: {e}")
            return []
