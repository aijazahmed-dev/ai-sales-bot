from pydantic import BaseModel, EmailStr, StringConstraints, Field
from datetime import datetime
from typing import Literal, Optional, Annotated

UserText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]

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

class MessageResponse(BaseModel):
    role: str
    content: str

class LeadResponse(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    intent_detected: bool
    created_at: datetime

class DashboardStatsResponse(BaseModel):
    total_leads: int
    hot_leads: int
    total_chats: int
    conversion_rate: float

    class Config:
        from_attributes = True


# Chat schemas
class ChatStartRequest(BaseModel):
    content: UserText

class ChatStartResponse(BaseModel):
    session_token: str
    reply: str

class ChatMessageRequest(BaseModel):
    session_token: str = Field(min_length=20, max_length=64)
    content: UserText

class ChatReply(BaseModel):
    reply: str

