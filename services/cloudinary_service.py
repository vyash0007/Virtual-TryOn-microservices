"""Cloudinary service for image uploads"""
import cloudinary
import cloudinary.uploader
from PIL import Image
from io import BytesIO
from fastapi import HTTPException
import logging
from config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

logger = logging.getLogger(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)


async def upload_to_cloudinary(image: Image.Image, user_id: str, product_id: str) -> str:
    """Upload processed image to Cloudinary and return secure URL"""
    try:
        # Save image to temporary buffer
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Upload to Cloudinary
        # public_id format: {product_id}_{user_id}
        public_id = f"{product_id}_{user_id}"
        
        logger.info(f"Uploading to Cloudinary: public_id={public_id}")
        response = cloudinary.uploader.upload(
            buffer,
            folder="ecommerce-products/users",
            public_id=public_id,
            resource_type="image",
            format="png"
        )
        
        secure_url = response["secure_url"]
        logger.info(f"Uploaded to Cloudinary: {secure_url}")
        return secure_url
    except Exception as e:
        logger.error(f"Error uploading to Cloudinary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image to Cloudinary: {str(e)}")

