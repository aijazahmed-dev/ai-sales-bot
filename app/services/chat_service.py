from sqlalchemy.orm import Session
from app.crud.chat import create_message
from app.services.llm_service import generate_response
from app.models.models import Lead
from app.crud.lead import mark_lead_as_interested, update_lead_info
from .intent_service import detect_intent
from app.utils.helpers import extract_user_info
from app.schemas.schemas import LeadUpdate
from app.utils.helpers import try_notify_human
from app.crud.lead import get_chat_history

SYSTEM_PROMPT = """
You are a helpful SEO expert sales assistant for a digital marketing company.

Rules:
- Keep replies short (3-5 sentences maximum).
- Be concise, conversational, professional, and persuasive.
- Do NOT write long explanations or blog-style content.
- Answer like a live chat agent, not a blog post.
- If the user greets or introduces themselves, reply with a friendly greeting and ask how you can help with SEO.
- If the user asks anything unrelated to SEO or digital marketing, politely apologize and say you can only help with SEO-related questions.
- Provide clear SEO advice only when an SEO-related question is asked.
- No bullet lists or headings.
- If the user shows clear buying intent (pricing, packages, hiring, contact), politely ask for contact details.
- After taking contact details say thanks/thank you we will reach out you within one to two hours.
"""

def handle_first_message(db: Session, message: str) -> int:
    # Create anonymous lead
    lead = Lead()
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Save first user message
    create_message(
        db=db,
        lead_id=lead.id,
        role="user",
        content=message
    )

    # Return lead id
    return lead.id

def process_message(db: Session, lead_id: int, user_message: str,):
    """
    1. Fetch chat history
    2. Build LLM messages
    3. Call LLM to get reply
    4. Save user and bot messages
    5. Detect buying intent and mark lead if needed
    """

    # Fetch chat history
    chat_history = get_chat_history(db, lead_id)

    # Build LLM messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    # Call LLM
    bot_reply = generate_response(messages)

    # Save messages
    create_message(db, lead_id, "user", user_message)

    # Extract & save user info
    user_info = extract_user_info(user_message)
    if any(user_info.values()):
        lead_update = LeadUpdate(**user_info)
        update_lead_info(db, lead_id, lead_update)
        try_notify_human(db, lead_id)

    # Detect intent (simple keyword check; can replace with AI intent detection later)
    if detect_intent(user_message):
        mark_lead_as_interested(db, lead_id)
        try_notify_human(db, lead_id)

    return bot_reply
