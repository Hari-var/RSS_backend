import json
import os
import uuid
from datetime import datetime
from fastapi import UploadFile
from azureblob import upload_stream_to_azure

# Create directories

os.makedirs("data", exist_ok=True)

EVENTS_FILE = "data/events.json"


def load_events():
    try:
        with open(EVENTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_events(events):
    with open(EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=2)

async def save_event(event_data, presenter_image: UploadFile = None, event_image: UploadFile = None):
    event_id = str(uuid.uuid4())
    
    # Save images
    presenter_path = None
    event_path = None
    
    if presenter_image and presenter_image.filename:
        presenter_filename = f"{event_id}_presenter_{presenter_image.filename}"
        presenter_path = await upload_stream_to_azure(await presenter_image.read(), presenter_filename, presenter_image.content_type)

    if event_image and event_image.filename:
        event_filename = f"{event_id}_event_{event_image.filename}"
        event_path = await upload_stream_to_azure(await event_image.read(), event_filename, event_image.content_type)
    
    # Create event record
    event_record = {
        "id": event_id,
        "event_type": event_data.get("eventType"),
        "event_name": event_data.get("eventName"),
        "presenter": event_data.get("presenter"),
        "date_time": event_data.get("dateTime"),
        "description": event_data.get("description"),
        "invite_location": event_data.get("inviteLocation"),
        "invite_link": event_data.get("inviteLink"),
        "presenter_images": presenter_path,
        "event_images": event_path,
        "created_at": datetime.now().isoformat()
    }
    
    # Save to JSON
    events = load_events()
    events.append(event_record)
    save_events(events)
    
    return event_record