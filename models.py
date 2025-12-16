from pydantic import BaseModel
from typing import List, Optional

class Event(BaseModel):
    event_type: str
    event_name: str
    description: Optional[str] = None
    date_time: str
    presenter: str
    presenter_images: Optional[str] = None
    event_images: Optional[str] = None
    invite_location: Optional[str] = None
    invite_link: Optional[str] = None

class Post(BaseModel):
    id: str
    title: str
    description: str
    image_url: Optional[str] = None
    link: str
    source: str
    published: str

class NewsletterRequest(BaseModel):
    posts: List[Post] = []
    events: List[Event] = []

class EmailRequest(BaseModel):
    posts: List[Post] = []
    events: List[Event] = []