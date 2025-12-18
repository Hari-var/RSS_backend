from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import json
from fastapi.middleware.cors import CORSMiddleware
from models import NewsletterRequest, EmailRequest
from rss_fetcher import fetch_rss_feeds
from template import generate_newsletter
from send_email import send_email
from event_handler import save_event, load_events
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def health_check():
    return {"status": "healthy"}

@app.get("/rss-updates")
def get_rss_updates():
    from posts_cache import get_cached_posts
    try:
        updates = get_cached_posts()
        return {"updates": updates, "count": len(updates)}
    except FileNotFoundError:
        return {"error": "source.json not found", "updates": [], "count": 0}
    except Exception as e:
        return {"error": str(e), "updates": [], "count": 0}




@app.post("/generate-newsletter")
def create_newsletter(request: NewsletterRequest):
    # print(request.posts)
    # print("======================")
    # print(request.events)
    combined = []
    combined.extend([posts.model_dump() for posts in request.posts])
    combined.extend([events.model_dump() for events in request.events])
    # Mark external events for template distinction
    for ext_event in request.external_events:
        ext_data = ext_event.model_dump()
        ext_data['is_external'] = True
        combined.append(ext_data)
    html_content = generate_newsletter(combined)
    return {"html": html_content, "status": "success"}

@app.post("/events")
async def create_event(
    event_type: str = Form(...),
    event_name: str = Form(...),
    presenter: str = Form(...),
    date_time: str = Form(...),
    invite_location: str = Form(...),
    description: str = Form(None),
    invite_link: str = Form(...),
    presenter_images: Optional[UploadFile] = File(None),
    event_images: Optional[UploadFile] = File(None)
):
    event_data = {
        "eventType": event_type,
        "eventName": event_name,
        "presenter": presenter,
        "dateTime": date_time,
        "description": description,
        "inviteLocation": invite_location,
        "inviteLink": invite_link
    }

    event_record = await save_event(event_data, presenter_images, event_images)
    return {"event": event_record, "status": "success"}

@app.get("/events")
def get_events():
    events = load_events()
    return {"events": events, "count": len(events)}

# @app.get("/uploads/events/{filename}")
# def get_event_image(filename: str):
#     return FileResponse(f"uploads/events/{filename}")

@app.get("/external-events")
async def get_external_events(num_results: int = 10):
    from external_events_cache import get_cached_external_events
    events = await get_cached_external_events(num_results)
    return {"events": events, "count": len(events)}

@app.post("/send-newsletter")
def send_newsletter_email(request: EmailRequest):
    updates = []
    updates.extend([post.model_dump() for post in request.posts])
    updates.extend([event.model_dump() for event in request.events])
    # Mark external events for template distinction
    for ext_event in request.external_events:
        ext_data = ext_event.model_dump()
        ext_data['is_external'] = True
        updates.append(ext_data)
    html_content = generate_newsletter(updates)
    result = send_email(html_content, ["Hari.Ponnamanda@valuemomentum.com"], "Generative AI Newsletter")
    return result

