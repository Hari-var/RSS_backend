import feedparser
import json
from datetime import datetime, timedelta
 
def fetch_rss_feeds(feed_urls, days_to_check=7):
    # Calculate the cutoff date for the last week
    cutoff_date = datetime.now() - timedelta(days=days_to_check)
    keywords = ['llm', 'transformer', 'fine-tuning', 'rag', 'vector db', 'gen-ai', 'model architecture', 'artificial intelligence', 'machine learning', 'ai', 'artificial-intelligence', 'deep learning', 'neural network', 'gpt', 'bert', 'chatbot', 'nlp', 'computer vision', 'reinforcement learning', 'supervised learning', 'unsupervised learning', 'generative ai', 'foundation model', 'large language model', 'embedding', 'attention mechanism', 'backpropagation', 'gradient descent', 'convolutional neural network', 'cnn', 'rnn', 'lstm', 'gru', 'autoencoder', 'gan', 'diffusion model', 'prompt engineering', 'zero-shot', 'few-shot', 'transfer learning', 'federated learning', 'mlops', 'model training', 'inference', 'pytorch', 'tensorflow', 'hugging face', 'openai', 'meta', 'google ai', 'anthropic', 'nvidia', 'microsoft ai', 'amazon ai', 'deepmind', 'claude', 'gemini', 'llama', 'chatgpt']
    
    weekly_updates = []
    for url in feed_urls:
        print(f"Processing: {url}")
        feed = feedparser.parse(url)
        print(f"Found {len(feed.entries)} entries from {feed.feed.get('title', 'Unknown')}")
        
        for entry in feed.entries:
            # Check if the entry was published within the last week
            if hasattr(entry, 'published_parsed'):
                published_time = datetime(*entry.published_parsed[:6])
                if published_time > cutoff_date:
                    # Check if title contains any of the keywords
                    if any(keyword.lower() in entry.title.lower() for keyword in keywords):
                        weekly_updates.append({
                            'title': entry.title,
                            'link': entry.link,
                            'source': feed.feed.title,
                            'published': published_time.strftime('%Y-%m-%d')
                        })
        print(f"Added {len([u for u in weekly_updates if u['source'] == feed.feed.get('title', 'Unknown')])} recent entries")
    return weekly_updates
 
# Load RSS feeds from source.json
with open('source.json', 'r') as f:
    sources = json.load(f)
RSS_FEEDS = list(sources.values()) 
all_updates = fetch_rss_feeds(RSS_FEEDS)

print(all_updates[0].keys())

#send all_updates to txt file
# with open('rss_updates.txt', 'a', encoding='utf-8') as f:
#     // "Computer Weekly":"https://www.computerweekly.com/rss/All-Computer-Weekly-content.xml",
#     for update in all_updates:
#         f.write(f"Title: {update['title']}\n")
#         f.write(f"Link: {update['link']}\n")
#         # f.write(f"Source: {update['source']}\n")
#         f.write(f"Published: {update['published']}\n")
        
        
#         f.write("\n")
# # print(all_updates)