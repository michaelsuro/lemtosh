from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import traceback
from app.services.auth import get_current_user
from app.services.llm import get_llm_response
from app.models.user import User

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    model: str

@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        print(f"[Chat] Received request from user {current_user.username}")
        print(f"[Chat] Message: {request.message}")
        print(f"[Chat] Selected model: {request.model}")
        
        # Check model status
        status = llm_service.get_model_status(request.model)
        print(f"[Chat] Model status: {status}")
        
        if status.get("status") != "ready":
            raise HTTPException(
                status_code=503,
                detail=f"Model is not ready. Current status: {status.get('status')}"
            )
        
        try:
            response = await get_llm_response(request.message, request.model)
            return {"response": response}
        except Exception as model_error:
            print(f"[Chat] Model error: {str(model_error)}")
            print("[Chat] Model error traceback:")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Error generating response: {str(model_error)}"
            )
            
    except HTTPException as http_error:
        # Re-raise HTTP exceptions
        raise http_error
    except Exception as e:
        print(f"[Chat] Unexpected error: {str(e)}")
        print("[Chat] Full traceback:")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )