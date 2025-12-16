import os
from azure.storage.blob import BlobClient, ContentSettings 
from config import MY_SAS_URL, CONTAINER_NAME

async def upload_stream_to_azure(file_stream, file_name, content_type):
    """
    Uploads a file stream directly to Azure without saving to disk first.
    """
    try:
        # 1. Parse SAS URL
        if "?" not in MY_SAS_URL:
            raise ValueError("Invalid SAS URL")
        
        base_url, sas_token = MY_SAS_URL.split("?", 1)
        
        # 2. Construct the full URL
        full_blob_url = f"{base_url.rstrip('/')}/{CONTAINER_NAME}/{file_name}?{sas_token}"
        
        # 3. Create Blob Client
        blob_client = BlobClient.from_blob_url(blob_url=full_blob_url)
        
        print(f"Uploading {file_name}...")

        # 4. Upload the stream directly
        # We use the dynamic content_type from the uploaded file
        blob_client.upload_blob(
            file_stream, 
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type)
        )
        
        # Return the public URL (without the SAS token for security)
        return f"{base_url.rstrip('/')}/{CONTAINER_NAME}/{file_name}"
    except Exception as e:
        print(f"Error: {e}")
        raise e

# def upload_to_azure(account_sas_url, container_name, local_file_path):
#     try:
#         file_name = os.path.basename(local_file_path)

#         if "?" not in account_sas_url:
#             raise ValueError("Your SAS URL is missing the token")
            
#         base_url, sas_token = account_sas_url.split("?", 1)
#         full_blob_url = f"{base_url.rstrip('/')}/{container_name}/{file_name}?{sas_token}"

#         print(f"Targeting: {base_url.rstrip('/')}/{container_name}/{file_name}")

#         blob_client = BlobClient.from_blob_url(blob_url=full_blob_url)
        
#         print("Uploading with Content-Type: image/jpg...")
        
#         with open(local_file_path, "rb") as data:
#             # 2. Pass content_settings inside the upload function
#             blob_client.upload_blob(
#                 data, 
#                 overwrite=True,
#                 content_settings=ContentSettings(content_type="image/jpg")
#             )
            
#         print("✅ Upload successful!")

#     except Exception as e:
#         print(f"❌ Error: {e}")

# # ================= CONFIGURATION =================

 
# LOCAL_FILE = r"C:\practice\RSS Feed\RSS_backend\img\pexels-cottonbro-6153354.jpg"

# upload_to_azure(MY_SAS_URL, CONTAINER_NAME, LOCAL_FILE)