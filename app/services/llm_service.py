from google import genai
from google.genai import types
from app.config import settings

# Create Gemini client once (recommended)
client = genai.Client(api_key=settings.LLM_API_KEY)

MODEL_NAME = "gemini-2.5-flash"


def generate_response(messages: list) -> str:
    """
    messages example:
    [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
    """

    # Convert messages into a single prompt (Gemini-compatible)
    prompt_parts = []

    for msg in messages:
        role = msg["role"].upper()
        content = msg["content"]
        prompt_parts.append(f"{role}: {content}")

    prompt = "\n".join(prompt_parts)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=100,
            temperature=0.3
        )   
    )

    return response.text.strip()
