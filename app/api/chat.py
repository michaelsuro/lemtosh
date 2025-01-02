from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.auth import get_current_user
from app.services.llm import get_llm_response

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    model: str

@router.post("/chat")
async def chat(
    message: ChatMessage,
    current_user = Depends(get_current_user)
):
    try:
        response = await get_llm_response(message.message, message.model)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))