from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Literal, Optional

class LeadCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    message: Optional[str] = None

class LeadUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    intent_detected: bool | None = None

class LeadResponse(LeadCreate):
    id: int
    intent_detected: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Chat schemas
class ChatStartRequest(BaseModel):
    content: str

class ChatMessageCreate(BaseModel):
    lead_id: int
    role: Literal["user", "bot"]
    content: str

class ChatMessageResponse(ChatMessageCreate):
    id: int
    lead_id: int
    created_at: datetime

    class Config:
        from_attributes = True