import os
import feedparser
import requests
from datetime import datetime, timedelta
import time
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        self.seen_urls = set()

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
            # Deduplication
            if entry.link in self.seen_urls:
                continue
            self.seen_urls.add(entry.link)
            
            # Time filtering (approximated as pubDate parsing can be tricky, we try basic standard format)
            published_parsed = entry.get('published_parsed')
            if published_parsed:
                published_dt = datetime.fromtimestamp(time.mktime(published_parsed))
                if published_dt < cutoff_time:
                    continue
            
            articles.append({
                "title": entry.title,
                "url": entry.link,
                "source": entry.source.title if hasattr(entry, 'source') else "Unknown",
                "date": entry.published,
                "content": entry.summary if hasattr(entry, 'summary') else entry.title
            })
            
            # Limit to top 10 per topic to avoid connecting indefinitely
            if len(articles) >= 10:
                break
                
        logger.info(f"Found {len(articles)} articles for {topic}")
        return articles

    def fetch_news_gnews(self, topic, lookback_hours=48):
        """
        Fetches news for a given topic using GNews API.
        """
        api_key = os.getenv("GNEWS_API_KEY")
        if not api_key:
            logger.error("GNEWS_API_KEY not found in environment variables.")
            return []

        # GNews expects 'q' parameter. Start/End dates can be supported but their format is specific.
        # We'll just fetch top results.
        
        # NOTE: GNews "search" endpoint
        url = "https://gnews.io/api/v4/search"
        
        # Calculate from date (ISO 8601 format: 2023-01-01T00:00:00Z)
        # GNews free tier might have restrictions, but we try standard param.
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
                # Deduplication
                if entry["url"] in self.seen_urls:
                    continue
                self.seen_urls.add(entry["url"])
                
                articles.append({
                    "title": entry["title"],
                    "url": entry["url"],
                    "source": entry["source"]["name"],
                    "date": entry["publishedAt"],
                    "content": entry["description"]
                })
            
            logger.info(f"Found {len(articles)} articles for {topic} via GNews")
            return articles

        except Exception as e:
            logger.error(f"Failed to fetch from GNews for {topic}: {e}")
            return []
