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
    content: str

class ChatMessageCreate(BaseModel):
    lead_id: int
    role: Literal["user", "bot"]
    content: str

class ChatMessageResponse(ChatMessageCreate):
    id: int
    lead_id: int
    created_at: datetime

# Admin login
class AdminLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True