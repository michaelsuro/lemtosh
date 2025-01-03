from fastapi import APIRouter, Depends
from app.config import settings
from app.services.auth import get_current_user
from app.services.llm import llm_service

router = APIRouter()

@router.get("/models")
async def get_models(current_user = Depends(get_current_user)):
    """Get available models and their status"""
    available_models = settings.get_available_models()
    
    # Add debug logging
    print("Getting model status")
    
    # Add status for each model
    for model_id in available_models:
        status = llm_service.get_model_status(model_id)
        print(f"Status for {model_id}:", status)  # Debug print
        available_models[model_id]["status"] = status
    
    return available_models