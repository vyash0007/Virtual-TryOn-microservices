"""Pydantic models for request/response"""
from pydantic import BaseModel
from typing import Dict


class TrialRequest(BaseModel):
    user_id: str
    email: str
    garment_images: Dict[str, str]  # {"product_id": "image_url"}
    person_image: str  # Person image URL


class PremiumRequest(BaseModel):
    user_id: str
    email: str
    garment_images: Dict[str, str]  # {"product_id": "image_url"}
    person_image: str  # Person image URL

