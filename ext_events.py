import requests
from datetime import datetime
from config import eve_api_key as api_key, cx

async def get_ai_events_india(num_results=30):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cx,
        'q': 'AI conference OR summit OR meetup India 2025 2026',
        'num': num_results
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        events = data.get('items', [])
        
        formatted_events = []
        for item in events:
            event = {
                "event_name": item.get('title', 'Unknown Event'),
                "event_type": "Tech Conference",
                "presenter": "TBD",
                "date_time": "2025-12-31T10:00:00Z",
                "invite_location": "India",
                "invite_link": item.get('link', ''),
                "description": item.get('snippet', ''),
                "event_images": item.get('pagemap', {}).get('cse_image', [{}])[0].get('src', '')
            }
            formatted_events.append(event)
        
        return formatted_events
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []
 
# Usage
# events = get_ai_events_india(API_KEY, CX)
# print(events)
# for event in events[:3]:
#     print(f"Event: {event['event_name']}")
#     print(f"Link: {event['invite_link']}")
#     print(f"Description: {event['description'][:100]}...\n")