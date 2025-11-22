"""Virtual try-on processing service"""
from typing import Dict
from PIL import Image
import logging
from services.image_service import download_image
from services.modal_service import process_tryon_batch_with_modal
from services.cloudinary_service import upload_to_cloudinary
from config import MODAL_ENDPOINT

logger = logging.getLogger(__name__)


async def process_virtual_tryon(user_id: str, garment_images: Dict[str, str], person_image: str) -> Dict[str, str]:
    """Download images, process try-on using batch endpoint, and save results"""
    logger.info(f"Starting try-on processing for user: {user_id}")
    
    # Download person image
    logger.info(f"Downloading person image from: {person_image}")
    person_img = await download_image(person_image)
    
    # Download all garment images
    garment_img_dict = {}
    for product_id, garment_url in garment_images.items():
        logger.info(f"Downloading garment {product_id} from: {garment_url}")
        garment_img = await download_image(garment_url)
        garment_img_dict[product_id] = garment_img
    
    # Process all garments in batch using Modal
    if MODAL_ENDPOINT:
        logger.info(f"Processing {len(garment_img_dict)} garments in batch via Modal")
        result_images = await process_tryon_batch_with_modal(person_img, garment_img_dict, MODAL_ENDPOINT)
    else:
        logger.warning("Modal endpoint not configured. Using placeholder.")
        # Fallback: return original person image for each product
        result_images = {product_id: person_img.copy() for product_id in garment_img_dict.keys()}
    
    # Upload all processed images to Cloudinary
    processed_images = {}
    for product_id, result_img in result_images.items():
        secure_url = await upload_to_cloudinary(result_img, user_id, product_id)
        processed_images[product_id] = secure_url
        logger.info(f"Uploaded processed image for product: {product_id}")
    
    logger.info(f"Completed batch processing for user: {user_id}")
    return processed_images

