import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import requests
import openai
from src.utils import is_spam, generate_context_reply

openai.api_key = os.getenv("OPENAI_API_KEY")
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
PAGE_ID = os.getenv("FB_PAGE_ID")


def generate_reply(text: str) -> str:
    """Generate a context-aware reply with CTA."""
    return generate_context_reply(text)


def list_recent_comments():
    if not (ACCESS_TOKEN and PAGE_ID):
        print("Facebook credentials not configured.")
        return []
    url = f"https://graph.facebook.com/v17.0/{PAGE_ID}/comments"
    r = requests.get(url, params={"access_token": ACCESS_TOKEN})
    if r.ok:
        return r.json().get("data", [])
    return []


def reply_to_comment(comment_id: str, message: str):
    url = f"https://graph.facebook.com/v17.0/{comment_id}/comments"
    requests.post(url, data={"message": message, "access_token": ACCESS_TOKEN})


def auto_reply():
    for comment in list_recent_comments():
        message = comment.get("message", "")
        if is_spam(message):
            continue
        reply = generate_reply(message)
        reply_to_comment(comment["id"], reply)
        print("Replied to comment", comment["id"])


if __name__ == "__main__":
    auto_reply()
