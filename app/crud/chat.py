from sqlalchemy.orm import Session
from app.models.models import ChatMessage

def create_message(db: Session, lead_id: int, role: str, content: str):
    msg = ChatMessage(
        lead_id=lead_id,
        role=role,
        content=content
    )
    
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_messages_by_lead_id(db: Session, lead_id: int):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.lead_id == lead_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
