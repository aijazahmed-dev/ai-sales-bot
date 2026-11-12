from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.crud.lead import get_lead_by_token
from app.db.database import get_db
from app.rate_limit import limiter
from app.schemas.schemas import (
    ChatMessageRequest,
    ChatReply,
    ChatStartRequest,
    ChatStartResponse,
)
from app.services.chat_service import (
    LeadNotFound,
    RateLimited,
    create_anonymous_lead,
    process_message,
)

router = APIRouter(prefix="/chat", tags=["Chat"])

TOO_MANY = "You're sending messages too fast. Please wait a few minutes and try again."


# NOTE: slowapi needs the parameter to be named exactly "request".
@router.post("/", response_model=ChatStartResponse)
@limiter.limit("5/minute;30/hour")
def start_chat(
    request: Request,
    payload: ChatStartRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Start a chat. Returns a secret session_token (NOT the numeric lead id) and the first reply."""
    lead = create_anonymous_lead(db)
    bot_msg = process_message(db, lead.id, payload.content, background_tasks)
    return ChatStartResponse(session_token=lead.session_token, reply=bot_msg.content)


@router.post("/message", response_model=ChatReply)
@limiter.limit("20/minute;200/hour")
def send_message(
    request: Request,
    payload: ChatMessageRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Continue a chat using the session_token from /chat/."""
    lead = get_lead_by_token(db, payload.session_token)
    if not lead:
        # Same answer for "wrong token" and "expired": reveals nothing.
        raise HTTPException(status_code=404, detail="Chat not found")

    try:
        bot_msg = process_message(db, lead.id, payload.content, background_tasks)
    except (LeadNotFound, RateLimited) as exc:
        if isinstance(exc, RateLimited):
            raise HTTPException(status_code=429, detail=TOO_MANY)
        raise HTTPException(status_code=404, detail="Chat not found")

    return ChatReply(reply=bot_msg.content)
