from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
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
        print(f"Received chat request: {request.message}")  # Debug print
        print(f"Using model: {request.model}")  # Debug print
        response = await get_llm_response(request.message, request.model)
        print(f"Generated response: {response}")  # Debug print
        return {"response": response}
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")  # Debug print
        raise HTTPException(status_code=500, detail=str(e))