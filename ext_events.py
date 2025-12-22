import requests
from datetime import datetime
from config import eve_api_key as api_key, cx




import requests
import re

def format_event_date(date_str):
    """
    Cleans natural language dates into a standard YYYY-MM-DD format.
    Handles formats like 'February 19–20, 2026' or 'March 13, 2026'.
    """
    try:
        # Remove ranges (e.g., '19–20' becomes '19') to get a single start date
        clean_date = re.sub(r'–\d+', '', date_str) 
        # Convert 'February 19, 2026' to datetime object
        dt = datetime.strptime(clean_date, '%B %d, %Y')
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    except:
        # If it's already a specific year, return a placeholder for early in that year
        if "2026" in date_str:
            return "2026-01-01T09:00:00Z"
        return "2025-12-31T10:00:00Z" # Default fallback

async def get_ai_events_india(num_results=10):
    # ... (params and request setup same as your code) ...
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cx,
        'q': 'Upcoming AI conference OR webinars OR summit OR meetup by google or microsoft or OpenAI in India in 2026',
        'num': num_results
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        events = data.get('items', [])
        
        formatted_events = []
        for item in events:
            pagemap = item.get('pagemap', {})
            metatags = pagemap.get('metatags', [{}])[0]
            
            # Logic to extract the raw date string from description or snippets
            raw_date = "2026" # Default
            snippet = item.get('snippet', '')
            
            # Extracting date using Regex from the snippet (e.g., February 19-20, 2026)
            date_match = re.search(r'([A-Z][a-z]+ \d{1,2}(?:–\d{1,2})?, 2026)', item.get('title', '') + " " + snippet)
            if date_match:
                raw_date = date_match.group(1)

            event = {
                "event_name": item.get('title', 'Unknown Event'),
                "event_type": "Technical Conference",
                "presenter": pagemap.get('organization', [{}])[0].get('name') or metatags.get('og:site_name', 'Tech Industry'),
                
                # Use the helper to format the date
                "date_time": format_event_date(raw_date),
                
                "invite_location": "India" if "India" in snippet or "India" in item.get('title') else "Global/Online",
                "invite_link": item.get('link', ''),
                "description": snippet,
                "event_images": pagemap.get('cse_image', [{}])[0].get('src', '')
            }
            formatted_events.append(event)
        
        return formatted_events
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

# Usage example
# events = await get_ai_events_india()
 
# Usage
async def main():
    events = await get_ai_events_india()
    print(events)
    for event in events[:3]:
        print(f"Event: {event['event_name']}")
        print(f"Link: {event['invite_link']}")
        print(f"Description: {event['description'][:100]}...\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
