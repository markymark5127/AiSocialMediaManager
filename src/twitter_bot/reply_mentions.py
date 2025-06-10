
import os
import sys
import tweepy
import openai
import time

# Allow running this script directly via `python src/twitter_bot/reply_mentions.py`
# by adding the repository root to `sys.path` so that `src` can be imported.
# Add the repository root to ``sys.path`` so imports work when executed directly
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)

from src.utils import is_spam, generate_context_reply

openai.api_key = os.getenv("OPENAI_API_KEY")

auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_SECRET")
)
api = tweepy.API(auth)

def get_mentions(since_id):
    return api.mentions_timeline(since_id=since_id, tweet_mode='extended')

def generate_reply(text: str) -> str:
    """Generate a context-aware reply with CTA."""
    return generate_context_reply(text)

def reply_to_mentions():
    since_id = int(open("since_id.txt", "r").read()) if os.path.exists("since_id.txt") else 1
    mentions = get_mentions(since_id)
    for mention in reversed(mentions):
        if is_spam(mention.full_text):
            continue
        print(f"Replying to @{mention.user.screen_name}")
        reply_text = generate_reply(mention.full_text)
        api.update_status(
            status=f"@{mention.user.screen_name} {reply_text}",
            in_reply_to_status_id=mention.id
        )
        since_id = max(since_id, mention.id)
    with open("since_id.txt", "w") as f:
        f.write(str(since_id))

if __name__ == "__main__":
    reply_to_mentions()
