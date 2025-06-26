import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

cloudinary_config = cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
    api_key = os.getenv("CLOUDINARY_API_KEY"), 
    api_secret = os.getenv("CLOUDINARY_SECRET_KEY")
)

def upload_video_to_cloudinary(video_path:str,public_id:str) -> str:
    response = cloudinary.uploader.upload_large(
        video_path,
        resource_type = "video",
        public_id = public_id,
        folder="manim-videos",
        chunk_size=6000000,
        overwrite=True
    )
    return response["secure_url"]
