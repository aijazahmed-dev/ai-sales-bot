from sqlalchemy.orm import Session
from app.crud.chat import create_message, get_messages_by_lead_id
from app.services.llm_service import generate_response
from app.models.models import Lead
from app.crud.lead import mark_lead_as_interested

SYSTEM_PROMPT = """
You are a helpful SEO expert sales assistant for a digital marketing company.

Rules:
- Keep replies very short (1-3 sentences maximum).
- Be concise, conversational, professional, and persuasive.
- Do NOT write long explanations or blog-style content.
- Answer like a live chat agent, not a blog post.
- If the user greets or introduces themselves, reply with a friendly greeting and ask how you can help with SEO.
- If the user asks anything unrelated to SEO or digital marketing, politely apologize and say you can only help with SEO-related questions.
- Provide clear SEO advice only when an SEO-related question is asked.
- No bullet lists or headings.
- If the user shows clear buying intent (pricing, packages, hiring, contact), politely ask for contact details.
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
    messages = get_messages_by_lead_id(db, lead_id)
    return [{"role": m.role, "content": m.content} for m in messages]

def process_message(db: Session, lead_id: int, user_message: str,):
    """
    1. Fetch chat history
    2. Build LLM messages
    3. Call LLM to get reply
    4. Save user and bot messages
    5. Detect buying intent and mark lead if needed
    """

    # 1️⃣ Fetch chat history
    chat_history = get_chat_history(db, lead_id)

    # 2️⃣ Build LLM messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    # 3️⃣ Call LLM
    bot_reply = generate_response(messages)

    # 4️⃣ Save messages
    create_message(db, lead_id, "user", user_message)
    # create_message(db, lead_id, "bot", bot_reply)

    # 5️⃣ Detect intent (simple keyword check; can replace with AI intent detection later)
    buy_keywords = ["buy", "purchase", "order", "sign up", "price", "pricing", "cost", "hire", "contact", "package", "service"]
    if any(word in user_message.lower() for word in buy_keywords):
        mark_lead_as_interested(db, lead_id)

    return bot_reply
