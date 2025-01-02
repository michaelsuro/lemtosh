from fastapi import APIRouter, Depends
from app.config import settings
from app.services.auth import get_current_user

router = APIRouter()

@router.get("/models")
async def get_models(current_user = Depends(get_current_user)):
    """Get available models for the current environment."""
    return settings.get_available_models()