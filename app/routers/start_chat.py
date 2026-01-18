from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.chat_service import handle_first_message
from app.schemas.schemas import ChatStartRequest

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/start")
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