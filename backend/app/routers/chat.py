from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ..database import get_db
from ..schemas import ChatMessageRequest, ChatMessageResponse
from ..models import ChatbotSession, ChatbotMessage
from ..services.chatbot_service import ChatbotService

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatMessageResponse)
def send_chat_message(payload: ChatMessageRequest, db: Session = Depends(get_db)):
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    result = ChatbotService.process_chat(
        db=db,
        message=payload.message.strip(),
        session_id=payload.session_id,
        context=payload.context
    )
    return ChatMessageResponse(**result)

@router.get("/history/{session_id}")
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    session_rec = db.query(ChatbotSession).filter(ChatbotSession.id == session_id).first()
    if not session_rec:
        return {"session_id": session_id, "messages": []}

    messages = (
        db.query(ChatbotMessage)
        .filter(ChatbotMessage.session_id == session_id)
        .order_by(ChatbotMessage.created_at)
        .all()
    )

    return {
        "session_id": session_id,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "message": m.message,
                "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else "N/A"
            }
            for m in messages
        ]
    }
