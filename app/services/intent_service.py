BUYING_KEYWORDS = ["order", "buy", "subscribe", "service", "pricing"]

def detect_intent(message: str) -> bool:
    message = message.lower()
    return any(word in message for word in BUYING_KEYWORDS)
