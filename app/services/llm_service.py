from dotenv import load_dotenv
import os

load_dotenv()

def generate_response(messages, engine="chatgpt"):
    if engine == "chatgpt":
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("LLM_API_KEY"))
        model = "gpt-4-turbo"
    else:  # Gemini
        from openai import OpenAI
        client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/"
        )
        model = "gemini-1.5-flash"

    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content
