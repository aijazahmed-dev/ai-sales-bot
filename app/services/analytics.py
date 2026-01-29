from sqlalchemy.orm import Session
from app.models.models import Lead, ChatMessage
from datetime import datetime

def get_stats(
    db: Session,
    start_date: datetime = None,
    end_date: datetime = None,
    hot_only: bool = False
):
    query = db.query(Lead)

    # Apply date filters
    if start_date:
        query = query.filter(Lead.created_at >= start_date)
    if end_date:
        query = query.filter(Lead.created_at <= end_date)

    # Apply hot leads filter if needed
    if hot_only:
        query = query.filter(Lead.intent_detected == True)

    total_leads = query.count()
    
    # Count hot leads separately if hot_only is False
    if not hot_only:
        hot_leads = query.filter(Lead.intent_detected == True).count()
    else:
        hot_leads = total_leads

    # Total chats for leads in this filter
    lead_ids = [lead.id for lead in query.all()]
    total_chats = db.query(ChatMessage).filter(ChatMessage.lead_id.in_(lead_ids)).count() if lead_ids else 0

    # Conversion rate
    conversion_rate = round((hot_leads / total_leads) * 100, 2) if total_leads else 0

    return {
        "total_leads": total_leads,
        "hot_leads": hot_leads,
        "total_chats": total_chats,
        "conversion_rate": conversion_rate
    }
