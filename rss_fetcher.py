import feedparser
import hashlib
import re
from datetime import datetime, timedelta

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
                        unique_id = hashlib.md5((entry.title + entry.link).encode()).hexdigest()[:8]
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