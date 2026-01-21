from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import ChatMessageCreate, ChatMessageResponse, ChatStartRequest
from app.crud.chat import create_message
from app.services.chat_service import process_message, handle_first_message


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/message", response_model=ChatMessageResponse)
def save_message(payload: ChatMessageCreate, db: Session = Depends(get_db)):
    """
    Save user message, generate AI reply, save AI reply, detect intent
    """
    try:
        ai_reply_text = process_message(db=db, lead_id=payload.lead_id, user_message=payload.content)
        bot_msg = create_message(db, payload.lead_id, "bot", ai_reply_text)
        return bot_msg
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/")
def start_chat(payload: ChatStartRequest, db: Session = Depends(get_db)):
    """
    Start a new chat:
    - Creates anonymous lead
    - Saves first message
    - Returns lead_id
    """
    lead_id = handle_first_message(db, payload.content)
    try:
        return {"lead_id": lead_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
