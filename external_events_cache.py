import json
import os
from datetime import datetime, timedelta
from ext_events import get_ai_events_india

CACHE_FILE = "data/external_events.json"

async def get_cached_external_events(num_results=10):
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Check if cache file exists and is recent
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache has data and timestamp
            if cache_data and 'timestamp' in cache_data and 'events' in cache_data:
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cache_time < timedelta(hours=5):
                    return cache_data['events']
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
    
    # Cache is empty, old, or invalid - fetch new data
    events = await get_ai_events_india(num_results)
    
    # Save to cache
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'events': events
    }
    
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    return events