import os
from dotenv import load_dotenv

load_dotenv()
smtp_host = "smtp.office365.com"
smtp_port = 587
smtp_user = "mvp@valuemomentum.club"
smtp_password = os.environ.get("smtp_password")
sender_email = "mvp@valuemomentum.club"
receiver_emails = ["Hari.Ponnamanda@valuemomentum.com"]
gemini_api_key = os.environ.get("GEMINI_API_KEY")
MY_SAS_URL = os.environ.get("sas_url")
CONTAINER_NAME = os.environ.get("container_name")