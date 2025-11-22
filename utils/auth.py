"""Authentication utilities"""
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import API_KEY
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API key from Bearer token"""
    if not API_KEY:
        logger.warning("API_KEY not configured. Authentication disabled.")
        return True
    
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

