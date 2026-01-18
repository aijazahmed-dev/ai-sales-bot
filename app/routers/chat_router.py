from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import ChatMessageCreate, ChatMessageResponse
from app.crud.chat import create_message

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/message", response_model=ChatMessageResponse)
def save_message(payload: ChatMessageCreate, db: Session = Depends(get_db)):
    """
    Save a chat message to the database
    """
    try:
        return create_message(
            db=db,
            lead_id=payload.lead_id,
            role=payload.role,
            content=payload.content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
