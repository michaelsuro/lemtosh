from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.chat import Chat, ChatMessage

async def create_new_chat(db: Session, user_id: int, model_name: str) -> Chat:
    """Create a new chat with auto-numbered title"""
    # Get the last chat number for this model
    last_chat = db.query(Chat).filter(
        Chat.user_id == user_id,
        Chat.model_name == model_name
    ).order_by(desc(Chat.created_at)).first()

    # Generate new chat number
    if last_chat:
        # Extract number from last chat title and increment
        last_num = int(last_chat.title.split('_')[-1])
        new_num = str(last_num + 1).zfill(2)
    else:
        new_num = "01"

    # Create new chat
    chat = Chat(
        title=f"{model_name}_{new_num}",
        model_name=model_name,
        user_id=user_id
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

async def add_message_to_chat(
    db: Session,
    chat_id: int,
    user_message: str,
    assistant_response: str
) -> ChatMessage:
    """Add a new message pair to the chat"""
    message = ChatMessage(
        chat_id=chat_id,
        user_message=user_message,
        assistant_response=assistant_response
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

async def get_chat_history(
    db: Session,
    chat_id: int,
    limit: int = None
) -> List[ChatMessage]:
    """Get chat history, optionally limited to recent messages"""
    query = db.query(ChatMessage).filter(
        ChatMessage.chat_id == chat_id
    ).order_by(ChatMessage.created_at)
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

async def get_user_chats(db: Session, user_id: int) -> List[Chat]:
    """Get all chats for a user"""
    return db.query(Chat).filter(
        Chat.user_id == user_id
    ).order_by(desc(Chat.updated_at)).all()

async def get_chat(db: Session, chat_id: int) -> Optional[Chat]:
    """Get a specific chat by ID"""
    return db.query(Chat).filter(Chat.id == chat_id).first()