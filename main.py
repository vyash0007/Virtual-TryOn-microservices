"""FastAPI application entry point"""
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import logging
from pathlib import Path

# Import schemas
from schemas import TrialRequest, PremiumRequest

# Import utilities
from utils.auth import verify_api_key

# Import actions
from actions.tryon_actions import process_and_send_email

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Create output directory for processed images (temporary, before Cloudinary upload)
OUTPUT_DIR = Path("processed_images")
OUTPUT_DIR.mkdir(exist_ok=True)


@app.post("/api/v1/trial")
async def trial_virtual_tryon(
    request: TrialRequest, 
    background_tasks: BackgroundTasks,
    verified: bool = Depends(verify_api_key)
):
    """Trial endpoint - max 2-3 images"""
    # Log request details
    logger.info(f"TRIAL ENDPOINT HIT")
    logger.info(f"User ID: {request.user_id}")
    logger.info(f"User Email: {request.email}")
    logger.info(f"Person Image URL: {request.person_image}")
    logger.info(f"Garment Images ({len(request.garment_images)}):")
    for product_id, image_url in request.garment_images.items():
        logger.info(f"  - Product ID: {product_id}, Image URL: {image_url}")
    
    total_images = len(request.garment_images) + 1  # +1 for person_image
    
    if total_images > 3:
        raise HTTPException(status_code=400, detail="Trial plan: max 3 total images allowed (garment + person)")
    
    # Return success immediately (fire and forget)
    # Processing will happen in background and email will be sent when done
    background_tasks.add_task(
        process_and_send_email,
        request.user_id,
        request.email,
        request.garment_images,
        request.person_image,
        "trial"
    )
    
    return {
        "success": True,
        "message": "Request received. Processing in background. You will receive an email with results shortly.",
        "user_id": request.user_id
    }


@app.post("/api/v1/premium")
async def premium_virtual_tryon(
    request: PremiumRequest, 
    background_tasks: BackgroundTasks,
    verified: bool = Depends(verify_api_key)
):
    """Premium endpoint - more images allowed"""
    # Log request details
    logger.info(f"PREMIUM ENDPOINT HIT")
    logger.info(f"User ID: {request.user_id}")
    logger.info(f"User Email: {request.email}")
    logger.info(f"Person Image URL: {request.person_image}")
    logger.info(f"Garment Images ({len(request.garment_images)}):")
    for product_id, image_url in request.garment_images.items():
        logger.info(f"  - Product ID: {product_id}, Image URL: {image_url}")
    
    # Return success immediately (fire and forget)
    # Processing will happen in background and email will be sent when done
    background_tasks.add_task(
        process_and_send_email,
        request.user_id,
        request.email,
        request.garment_images,
        request.person_image,
        "premium"
    )
    
    return {
        "success": True,
        "message": "Request received. Processing in background. You will receive an email with results shortly.",
        "user_id": request.user_id
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(exc.body)}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
