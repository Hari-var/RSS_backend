from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import json
from fastapi.middleware.cors import CORSMiddleware
from models import NewsletterRequest, EmailRequest
from rss_fetcher import fetch_rss_feeds
from template import generate_newsletter
from send_email import send_email
from event_handler import save_event, load_events
from typing import Optional
from pydantic import BaseModel
import bcrypt
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from config import MY_SAS_URL, CONTAINER_NAME, receiver_emails

class LoginRequest(BaseModel):
    username: str
    password: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "user"

class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

class UpdateEventRequest(BaseModel):
    event_type: Optional[str] = None
    event_name: Optional[str] = None
    presenter: Optional[str] = None
    date_time: Optional[str] = None
    invite_location: Optional[str] = None
    invite_link: Optional[str] = None

class UpdateConfigRequest(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    sender_email: Optional[str] = None
    receiver_emails: Optional[list] = None
    posts_cache_hours: Optional[int] = None
    events_cache_hours: Optional[int] = None

class AddSourceRequest(BaseModel):
    name: str
    url: str

class UpdateSourceRequest(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None


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

@app.put("/events/{event_id}")
def update_event(event_id: str, request: UpdateEventRequest):
    try:
        with open("data/events.json", "r") as f:
            events = json.load(f)
        
        event_found = False
        for event in events:
            if event["id"] == event_id:
                if request.event_type:
                    event["event_type"] = request.event_type
                if request.event_name:
                    event["event_name"] = request.event_name
                if request.presenter:
                    event["presenter"] = request.presenter
                if request.date_time:
                    event["date_time"] = request.date_time
                if request.invite_location:
                    event["invite_location"] = request.invite_location
                if request.invite_link:
                    event["invite_link"] = request.invite_link
                event_found = True
                break
        
        if not event_found:
            raise HTTPException(status_code=404, detail="Event not found")
        
        with open("data/events.json", "w") as f:
            json.dump(events, f, indent=2)
        
        return {"success": True, "message": "Event updated successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Events file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    try:
        with open("data/events.json", "r") as f:
            events = json.load(f)
        
        # Find event and delete associated images from blob
        event_to_delete = None
        for event in events:
            if event["id"] == event_id:
                event_to_delete = event
                break
        
        if event_to_delete:
            base_url, sas_token = MY_SAS_URL.split("?", 1)
            blob_service_client = BlobServiceClient(account_url=base_url, credential=sas_token)
            container_client = blob_service_client.get_container_client(CONTAINER_NAME)
            
            # Delete presenter image
            if event_to_delete.get("presenter_images"):
                blob_name = event_to_delete["presenter_images"].split("/")[-1]
                container_client.delete_blob(blob_name)
            
            # Delete event image
            if event_to_delete.get("event_images"):
                blob_name = event_to_delete["event_images"].split("/")[-1]
                container_client.delete_blob(blob_name)
        
        events = [event for event in events if event["id"] != event_id]
        
        with open("data/events.json", "w") as f:
            json.dump(events, f, indent=2)
        
        return {"success": True, "message": "Event deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Events file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/external-events")
async def get_external_events(num_results: int = 10):
    from external_events_cache import get_cached_external_events
    events = await get_cached_external_events(num_results)
    return {"events": events, "count": len(events)}

@app.get("/blob-images")
def get_blob_images():
    try:
        base_url, sas_token = MY_SAS_URL.split("?", 1)
        blob_service_client = BlobServiceClient(account_url=base_url, credential=sas_token)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        blobs = []
        for blob in container_client.list_blobs():
            blobs.append({
                "name": blob.name,
                "url": f"{base_url.rstrip('/')}/{CONTAINER_NAME}/{blob.name}",
                "size": blob.size,
                "last_modified": blob.last_modified.isoformat()
            })
        
        return {"images": blobs, "count": len(blobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config")
def get_config():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/config")
def update_config(request: UpdateConfigRequest):
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        if request.smtp_host:
            config["smtp_host"] = request.smtp_host
        if request.smtp_port:
            config["smtp_port"] = request.smtp_port
        if request.smtp_user:
            config["smtp_user"] = request.smtp_user
        if request.sender_email:
            config["sender_email"] = request.sender_email
        if request.receiver_emails:
            config["receiver_emails"] = request.receiver_emails
        if request.posts_cache_hours:
            config["posts_cache_hours"] = request.posts_cache_hours
        if request.events_cache_hours:
            config["events_cache_hours"] = request.events_cache_hours
        
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        return {"success": True, "message": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sources")
def get_sources():
    try:
        with open("source.json", "r") as f:
            sources = json.load(f)
        return {"sources": sources, "count": len(sources)}
    except FileNotFoundError:
        return {"sources": {}, "count": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sources")
def add_source(request: AddSourceRequest):
    try:
        with open("source.json", "r") as f:
            sources = json.load(f)
        
        if request.name in sources:
            raise HTTPException(status_code=400, detail="Source name already exists")
        
        sources[request.name] = request.url
        
        with open("source.json", "w") as f:
            json.dump(sources, f, indent=4)
        
        return {"success": True, "message": "Source added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/sources/{source_name}")
def update_source(source_name: str, request: UpdateSourceRequest):
    try:
        with open("source.json", "r") as f:
            sources = json.load(f)
        
        if source_name not in sources:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Handle name change
        if request.name and request.name != source_name:
            if request.name in sources:
                raise HTTPException(status_code=400, detail="New source name already exists")
            # Get the URL (use new URL if provided, otherwise keep existing)
            url_to_use = request.url if request.url else sources[source_name]
            # Remove old entry
            del sources[source_name]
            # Add new entry
            sources[request.name] = url_to_use
        elif request.url:
            # Only updating URL, keep same name
            sources[source_name] = request.url
        
        with open("source.json", "w") as f:
            json.dump(sources, f, indent=4)
        
        return {"success": True, "message": "Source updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sources/{source_name}")
def delete_source(source_name: str):
    try:
        with open("source.json", "r") as f:
            sources = json.load(f)
        
        if source_name not in sources:
            raise HTTPException(status_code=404, detail="Source not found")
        
        del sources[source_name]
        
        with open("source.json", "w") as f:
            json.dump(sources, f, indent=4)
        
        return {"success": True, "message": "Source deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    result = send_email(html_content, receiver_emails, "Generative AI Newsletter")
    return result
@app.post("/users")
def create_user(request: CreateUserRequest):
    try:
        with open("data/users.json", "r") as f:
            users = json.load(f)
        
        # Check if username already exists
        for user_data in users.values():
            if user_data["username"] == request.username:
                raise HTTPException(status_code=400, detail="Username already exists")
        
        # Generate new ID
        new_id = str(max([int(k) for k in users.keys()], default=0) + 1)
        
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
        
        users[new_id] = {
            "username": request.username,
            "role": request.role,
            "created_time": datetime.now().isoformat() + "Z",
            "encrypted_password": hashed_password.decode('utf-8')
        }
        
        with open("data/users.json", "w") as f:
            json.dump(users, f, indent=2)
        
        return {"success": True, "message": "User created successfully", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
def get_users():
    try:
        with open("data/users.json", "r") as f:
            users = json.load(f)
        
        user_list = []
        for user_id, user_data in users.items():
            user_list.append({
                "id": user_id,
                "username": user_data["username"],
                "role": user_data["role"],
                "created_time": user_data["created_time"]
            })
        
        return {"users": user_list, "count": len(user_list)}
    except FileNotFoundError:
        return {"users": [], "count": 0}

# @app.put("/users/{user_id}")
# def update_user(user_id: str, request: UpdateUserRequest):
#     try:
#         with open("data/users.json", "r") as f:
#             users = json.load(f)
        
#         if user_id not in users:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         # Check username uniqueness if updating username
#         if request.username:
#             for uid, user_data in users.items():
#                 if uid != user_id and user_data["username"] == request.username:
#                     raise HTTPException(status_code=400, detail="Username already exists")
#             users[user_id]["username"] = request.username
        
#         if request.password:
#             hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
#             users[user_id]["encrypted_password"] = hashed_password.decode('utf-8')
        
#         if request.role:
#             users[user_id]["role"] = request.role
        
#         with open("data/users.json", "w") as f:
#             json.dump(users, f, indent=2)
        
#         return {"success": True, "message": "User updated successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    try:
        with open("data/users.json", "r") as f:
            users = json.load(f)
        
        if user_id not in users:
            raise HTTPException(status_code=404, detail="User not found")
        
        del users[user_id]
        
        with open("data/users.json", "w") as f:
            json.dump(users, f, indent=2)
        
        return {"success": True, "message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    try:
        with open("data/users.json", "r") as f:
            users = json.load(f)
        
        # Find user by username
        user = None
        for user_data in users.values():
            if user_data["username"] == username:
                user = user_data
                break
        
        if not user:
            return {"success": False}
        
        # Check if password matches hashed password
        if bcrypt.checkpw(password.encode('utf-8'), user["encrypted_password"].encode('utf-8')):
            return {"success": True, "role": user["role"]}
        else:
            return {"success": False}
    except FileNotFoundError:
        return {"success": False}

