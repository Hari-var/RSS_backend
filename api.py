from fastapi import FastAPI
import feedparser
import json
import hashlib
import re
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Optional
from template import generate_newsletter
from send_email import send_email
import config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def fetch_rss_feeds(feed_urls, days_to_check=7):
    cutoff_date = datetime.now() - timedelta(days=days_to_check)
    keywords = ['llm', 'transformer', 'fine-tuning', 'rag', 'vector db', 'gen-ai', 'model architecture', 'artificial intelligence', 'machine learning', 'ai', 'artificial-intelligence', 'deep learning', 'neural network', 'gpt', 'bert', 'chatbot', 'nlp', 'computer vision', 'reinforcement learning', 'supervised learning', 'unsupervised learning', 'generative ai', 'foundation model', 'large language model', 'embedding', 'attention mechanism', 'backpropagation', 'gradient descent', 'convolutional neural network', 'cnn', 'rnn', 'lstm', 'gru', 'autoencoder', 'gan', 'diffusion model', 'prompt engineering', 'zero-shot', 'few-shot', 'transfer learning', 'federated learning', 'mlops', 'model training', 'inference', 'pytorch', 'tensorflow', 'hugging face', 'openai', 'meta', 'google ai', 'anthropic', 'nvidia', 'microsoft ai', 'amazon ai', 'deepmind', 'claude', 'gemini', 'llama', 'chatgpt','langchain','vectara','pinecone','weaviate','qdrant','chroma','lancedb','milvus','semantic kernel','mistral ai','xformers','flash attention','deepseek','retrieval augmented generation']
    
    weekly_updates = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if hasattr(entry, 'published_parsed'):
                published_time = datetime(*entry.published_parsed[:6])
                if published_time > cutoff_date:
                    if any(keyword.lower() in entry.title.lower() for keyword in keywords):
                        # Generate unique ID using hash of title and link
                        unique_id = hashlib.md5((entry.title + entry.link).encode()).hexdigest()[:8]
                        # Extract image URL if available
                        image_url = None
                        if hasattr(entry, 'image') and entry.image:
                            image_url = entry.image
                        elif hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                            image_url = entry.media_thumbnail[0].get('url')
                        elif hasattr(entry, 'media_content') and entry.media_content:
                            image_url = entry.media_content[0].get('url')
                        elif hasattr(entry, 'enclosures') and entry.enclosures:
                            for enclosure in entry.enclosures:
                                if hasattr(enclosure, 'type') and enclosure.type.startswith('image/'):
                                    image_url = enclosure.href
                                    break
                        
                        # Extract and clean description
                        description = ''
                        if hasattr(entry, 'description'):
                            description = re.sub(r'<[^>]+>', '', entry.description)
                            description = re.sub(r'\s+', ' ', description).strip()
                        elif hasattr(entry, 'summary'):
                            description = re.sub(r'<[^>]+>', '', entry.summary)
                            description = re.sub(r'\s+', ' ', description).strip()
                        
                        weekly_updates.append({
                            'id': unique_id,
                            'title': entry.title,
                            'description': description,
                            'image_url': image_url,
                            'link': entry.link,
                            'source': feed.feed.title,
                            'published': published_time.strftime('%Y-%m-%d')
                        })
    return weekly_updates

class events(BaseModel):
    event_type: str
    event_name: str
    description: Optional[str] = None
    date_time: str
    presenter: str
    presenter_images: Optional[str] = None
    event_images: Optional[str] = None
    invite_location: Optional[str] = None
    invite_link: Optional[str] = None


class posts(BaseModel):
    id: str
    title: str
    description: str
    image_url: Optional[str] = None
    link: str
    source: str
    published: str

class NewsletterRequest(BaseModel):
    posts: List[posts]
    events: List[events]

@app.get("/")
def health_check():
    return {"status": "healthy"}

@app.get("/rss-updates")
def get_rss_updates():
    try:
        with open('source.json', 'r') as f:
            sources = json.load(f)
    except FileNotFoundError:
        return {"error": "source.json not found", "updates": [], "count": 0}
    rss_feeds = list(sources.values())
    updates = fetch_rss_feeds(rss_feeds)
    updates.sort(key=lambda x: x['published'], reverse=True)
    return {"updates": updates, "count": len(updates)}

class EmailRequest(BaseModel):
    posts: List[posts]
    events: list[events]

@app.post("/generate-newsletter")
def create_newsletter(request: NewsletterRequest):
    combined = [post.model_dump() for post in request.posts]
    combined.extend([event.model_dump() for event in request.events])
    html_content = generate_newsletter(combined)
    return {"html": html_content, "status": "success"}

@app.post("/send-newsletter")
def send_newsletter_email(request: EmailRequest):
    updates = [post.model_dump() for post in request.posts]
    updates.extend([event.model_dump() for event in request.events])
    html_content = generate_newsletter(updates)
    result = send_email(html_content, config.receiver_emails, "Generative AI Newsletter")
    return result

