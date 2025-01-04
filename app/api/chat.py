from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import traceback

from app.database import get_db
from app.services.auth import get_current_user
from app.services.llm import llm_service, get_llm_response
from app.services.chat import (
    create_new_chat,
    add_message_to_chat,
    get_chat_history,
    get_user_chats,
    get_chat
)
from app.models.user import User

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    model: str
    chat_id: Optional[int] = None

@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        print(f"[Chat] Received request from user {current_user.username}")
        print(f"[Chat] Message: {request.message}")
        print(f"[Chat] Selected model: {request.model}")

        # Get or create chat
        if request.chat_id:
            chat = await get_chat(db, request.chat_id)
            if not chat or chat.user_id != current_user.id:
                raise HTTPException(status_code=404, detail="Chat not found")
        else:
            chat = await create_new_chat(db, current_user.id, request.model)

        # Get chat history
        history = await get_chat_history(db, chat.id)
        history_formatted = [
            {
                "user_message": msg.user_message,
                "assistant_response": msg.assistant_response
            }
            for msg in history
        ]

        # Generate response with timeout protection
        try:
            response = await get_llm_response(request.message, request.model, history_formatted)
        except Exception as e:
            print(f"[Chat] Model response error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate response. Please try again."
            )

        # Save message and response
        try:
            await add_message_to_chat(db, chat.id, request.message, response)
        except Exception as e:
            print(f"[Chat] Database error: {str(e)}")
            # Still return the response even if saving fails
            pass

        return {
            "response": response,
            "chat_id": chat.id
        }

    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        print(f"[Chat] Unexpected error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/chats", response_model=List[dict])
async def get_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chats for the current user"""
    chats = await get_user_chats(db, current_user.id)
    return [
        {
            "id": chat.id,
            "title": chat.title,
            "model": chat.model_name,
            "updated_at": chat.updated_at
        }
        for chat in chats
    ]

@router.get("/chats/{chat_id}/messages")
async def get_chat_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific chat"""
    chat = await get_chat(db, chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = await get_chat_history(db, chat_id)
    print(f"[Chat] Retrieved {len(messages)} messages for chat {chat_id}")  # Debug log
    
    return [
        {
            "user_message": msg.user_message,
            "assistant_response": msg.assistant_response,
            "created_at": msg.created_at.isoformat()  # Format date for JSON
        }
        for msg in messages
    ]