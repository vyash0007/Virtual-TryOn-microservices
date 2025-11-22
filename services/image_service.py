"""Image downloading and processing service"""
import httpx
from PIL import Image
from io import BytesIO
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


async def download_image(url: str) -> Image.Image:
    """Download image from URL and return PIL Image"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")
            logger.info(f"Downloaded image from: {url}")
            return img
    except Exception as e:
        logger.error(f"Error downloading image from {url}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to download image from URL: {str(e)}")

