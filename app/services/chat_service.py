from sqlalchemy.orm import Session
from app.crud.chat import create_message, get_messages_by_lead
from app.services.llm_service import generate_response
from app.models.models import Lead

SYSTEM_PROMPT = """
You are a helpful assistant SEO expert for a digital marketing company.
- Always provide clear SEO advice.
- Be professional and persuasive.
- If the user shows buying intent, ask for contact details.
"""

def handle_first_message(db: Session, message: str) -> int:
    # 1️⃣ Create anonymous lead
    lead = Lead()
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # 2️⃣ Save first user message
    create_message(
        db=db,
        lead_id=lead.id,
        role="user",
        content=message
    )

    # 3️⃣ Return lead id
    return lead.id

def get_chat_history(db: Session, lead_id: int):
    messages = get_messages_by_lead(db, lead_id)
    return [{"role": m.role, "content": m.content} for m in messages]

def process_message(
    db: Session,
    lead: Lead,
    user_message: str
):
    # 1️⃣ Fetch chat history
    chat_history = get_chat_history(db, lead.id)

    # 2️⃣ Build LLM messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    # 3️⃣ Call LLM
    bot_reply = generate_response(messages)

    # 4️⃣ Save messages
    create_message(db, lead.id, "user", user_message)
    create_message(db, lead.id, "bot", bot_reply)

    return bot_reply
