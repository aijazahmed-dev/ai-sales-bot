BUYING_KEYWORDS = [
    "order",
    "buy",
    "subscribe",
    "service",
    "pricing",
    "price",
    "cost",
    "hire",
    "contact",
    "package",
    "sign up"
]

def detect_intent(message: str) -> bool:
    """
    Detect buying intent based on keywords.
    Returns True if buying intent is detected.
    """
    message = message.lower()
    return any(keyword in message for keyword in BUYING_KEYWORDS)
