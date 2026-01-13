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
