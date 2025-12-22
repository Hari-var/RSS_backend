import os
import json
from dotenv import load_dotenv

load_dotenv()

# Load config from JSON
with open('config.json', 'r') as f:
    config = json.load(f)

smtp_host = config["smtp_host"]
smtp_port = config["smtp_port"]
smtp_user = config["smtp_user"]
smtp_password = os.environ.get("smtp_password")
sender_email = config["sender_email"]
receiver_emails = config["receiver_emails"]
gemini_api_key = os.environ.get("GEMINI_API_KEY")
MY_SAS_URL = os.environ.get("sas_url")
CONTAINER_NAME = os.environ.get("container_name")
eve_api_key = os.environ.get("event_api_key")
cx = os.environ.get("CX")
posts_cache_hours = config.get("posts_cache_hours", 24)
events_cache_hours = config.get("events_cache_hours", 5)
