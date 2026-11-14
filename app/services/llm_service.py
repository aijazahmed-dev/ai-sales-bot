import logging
from typing import Optional

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.LLM_API_KEY)

FALLBACK_REPLY = (
    "Sorry, I couldn't process that. Could you rephrase it, "
    "or leave your email so our team can follow up?"
)


class BotTurn(BaseModel):
    """What Gemini returns for every user message (one call = reply + analysis)."""

    reply: str = Field(
        description="Short, friendly live-chat reply to the visitor (max 2-3 sentences, plain text)."
    )
    buying_intent: bool = Field(
        description=(
            "True only if the visitor shows clear interest in buying/hiring: asks about "
            "pricing, packages, getting started, a quote, a call, or says they want to hire."
        )
    )
    needs_human: bool = Field(
        description=(
            "True if the visitor asks for a human, is upset, or asks something you cannot "
            "answer from the business info you were given."
        )
    )
    name: Optional[str] = Field(
        default=None,
        description="Visitor's name ONLY if they stated it themselves. Otherwise null.",
    )
    email: Optional[str] = Field(
        default=None,
        description="Visitor's email ONLY if they typed it in the chat. Never guess. Otherwise null.",
    )
    phone: Optional[str] = Field(
        default=None,
        description="Visitor's phone number ONLY if they typed it in the chat. Never guess. Otherwise null.",
    )
    summary: Optional[str] = Field(
        default=None,
        description="One short sentence: what this visitor wants. Null if nothing useful yet.",
    )


def _fallback_turn() -> BotTurn:
    return BotTurn(reply=FALLBACK_REPLY, buying_intent=False, needs_human=False)


def generate_turn(system_prompt: str, history: list[dict]) -> BotTurn:
    """
    history = [{"role": "user" | "bot", "content": "..."}, ...]
    The last item must be the newest user message.
    Never raises: on any failure returns a safe fallback turn.
    """
    contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part.from_text(text=m["content"])],
        )
        for m in history
    ]

    try:
        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=BotTurn,
                max_output_tokens=400,
                temperature=0.4,
                # Chatbot doesn't need deep reasoning: faster, cheaper, no truncation.
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
    except Exception:
        logger.exception("Gemini call failed")
        return _fallback_turn()

    turn = response.parsed
    if not isinstance(turn, BotTurn):
        # SDK couldn't parse; try the raw text ourselves.
        try:
            turn = BotTurn.model_validate_json(response.text or "")
        except Exception:
            reason = response.candidates[0].finish_reason if response.candidates else "no_candidates"
            logger.warning("Unparseable Gemini reply, finish_reason=%s", reason)
            return _fallback_turn()

    turn.reply = (turn.reply or "").strip() or FALLBACK_REPLY
    return turn
