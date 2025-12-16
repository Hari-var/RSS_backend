from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
import json
import os
from fastapi.middleware.cors import CORSMiddleware
 
app = FastAPI()

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Post(BaseModel):
    id: str
    title: str
    description: str
    image_url: Optional[str] = None
    link: str
    source: str
    published: str

class Event(BaseModel):
    event_type: str
    event_name: str
    description: Optional[str] = None
    date_time: str
    presenter: str
    invite_location: Optional[str] = None
    invite_link: Optional[str] = None
 
@app.post("/events")
async def create_newsletter(
    posts: Optional[str] = Form(None),
    events: Optional[List[str]] = Form(None),
    presenter_images: Optional[UploadFile] = File(None),
    event_images: Optional[UploadFile] = File(None)
):
    result = {"posts": [], "events": [], "status": "success", "image_urls": []}
    
    if posts:
        try:
            posts_data = json.loads(posts)
            result["posts"] = [Post(**post).model_dump() for post in posts_data]
        except Exception as e:
            result["error"] = f"Posts error: {str(e)}"
    
    if events:
        try:
            events_data = [json.loads(event) for event in events]
            result["events"] = [Event(**event).model_dump() for event in events_data]
        except Exception as e:
            result["error"] = f"Events error: {str(e)}"
    
    # Handle image uploads
    if presenter_images:
        try:
            filename = f"presenter_{presenter_images.filename}"
            with open(f"uploads/{filename}", "wb") as f:
                f.write(await presenter_images.read())
            result["image_urls"].append(f"/images/{filename}")
        except Exception as e:
            result["error"] = f"Presenter image error: {str(e)}"
    
    if event_images:
        try:
            filename = f"event_{event_images.filename}"
            with open(f"uploads/{filename}", "wb") as f:
                f.write(await event_images.read())
            result["image_urls"].append(f"/images/{filename}")
        except Exception as e:
            result["error"] = f"Event image error: {str(e)}"
    
    return result

@app.get("/images/{filename}")
async def get_image(filename: str):
    return FileResponse(f"uploads/{filename}")