import re
import openai
import os
from typing import Optional

openai.api_key = os.getenv("OPENAI_API_KEY")
FAQ_LINK = os.getenv("FAQ_LINK", "https://example.com/faq")

EMOJI_PATTERN = re.compile(r"^[\W_]+$")


def is_spam(text: str) -> bool:
    """Return True if text looks like spam or too short."""
    if not text or len(text.strip()) < 4:
        return True
    if EMOJI_PATTERN.fullmatch(text.strip()):
        return True
    spam_keywords = ["buy followers", "check my page", "subscribe"]
    lowered = text.lower()
    return any(kw in lowered for kw in spam_keywords)


def generate_context_reply(text: str) -> str:
    """Generate a short helpful reply with CTA linking to the FAQ."""
    prompt = (
        "You are a helpful social media assistant. "
        f"Answer the user question briefly and include a CTA to read the FAQ here: {FAQ_LINK}. "
        f"Question: {text}"
    )
    res = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return res["choices"][0]["message"]["content"].strip()
