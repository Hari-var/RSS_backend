import json
import os
from datetime import datetime, timedelta
from rss_fetcher import fetch_rss_feeds
from config import posts_cache_hours

CACHE_FILE = "data/posts_cache.json"

def get_cached_posts():
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Check if cache file exists and is recent
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache has data and timestamp
            if cache_data and 'timestamp' in cache_data and 'posts' in cache_data:
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cache_time < timedelta(hours=posts_cache_hours):
                    return cache_data['posts']
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
    
    # Cache is empty, old, or invalid - fetch new data
    with open('source.json', 'r') as f:
        sources = json.load(f)
    rss_feeds = list(sources.values())
    posts = fetch_rss_feeds(rss_feeds)
    posts.sort(key=lambda x: x['published'], reverse=True)
    
    # Save to cache
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'posts': posts
    }
    
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    return posts