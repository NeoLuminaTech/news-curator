import feedparser
import time
from datetime import datetime, timedelta
from urllib.parse import quote

def test_feed():
    query = "Red Sea shipping OR Suez Canal blockage OR Panama Canal drought"
    encoded_topic = quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-US&gl=US&ceid=US:en"
    print(f"Fetching: {rss_url}")
    
    feed = feedparser.parse(rss_url)
    print(f"Feed entries: {len(feed.entries)}")
    
    lookback_hours = 48
    cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
    print(f"Cutoff time: {cutoff_time}")

    count_valid_date = 0
    for i, entry in enumerate(feed.entries[:10]):
        print(f"\nEntry {i}: {entry.title}")
        print(f"Date: {entry.published}")
        published_parsed = entry.get('published_parsed')
        if published_parsed:
            published_dt = datetime.fromtimestamp(time.mktime(published_parsed))
            print(f"Parsed Date: {published_dt}")
            if published_dt < cutoff_time:
                print(">>> OLDER than cutoff")
            else:
                print(">>> RECENT (Keep)")
                count_valid_date += 1
        else:
            print(">>> NO DATE PARSED (Keep)")
            count_valid_date += 1
            
    print(f"\nTotal valid by date in top 10: {count_valid_date}")

if __name__ == "__main__":
    test_feed()
