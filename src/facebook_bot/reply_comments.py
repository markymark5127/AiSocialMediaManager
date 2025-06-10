import os
import requests
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
PAGE_ID = os.getenv("FB_PAGE_ID")


def generate_reply(text: str) -> str:
    prompt = f"Reply to this Facebook comment in a friendly tone: {text}"
    resp = openai.ChatCompletion.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
    return resp["choices"][0]["message"]["content"].strip()


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
        reply = generate_reply(comment.get("message", ""))
        reply_to_comment(comment["id"], reply)
        print("Replied to comment", comment["id"])


if __name__ == "__main__":
    auto_reply()
