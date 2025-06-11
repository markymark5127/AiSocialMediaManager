import os
import sys
import tweepy
import openai

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
    try:
        return api.mentions_timeline(since_id=since_id, tweet_mode='extended')
    except tweepy.TweepyException as e:
        print(f"❌ Error fetching mentions: {e}")
        return []

def generate_reply(text: str) -> str:
    return generate_context_reply(text)

def reply_to_mentions():
    # ✅ Safe load of since_id
    try:
        with open("since_id.txt", "r") as f:
            since_id = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        since_id = 1

    # ✅ Check auth explicitly
    try:
        user = api.verify_credentials()
        print(f"✅ Authenticated as @{user.screen_name}")
    except Exception as e:
        print(f"❌ Failed to authenticate: {e}")
        return

    mentions = get_mentions(since_id)
    print(f"📥 Found {len(mentions)} mentions")

    for mention in reversed(mentions):
        if is_spam(mention.full_text):
            print(f"🚫 Skipping spam from @{mention.user.screen_name}")
            continue

        print(f"💬 Replying to @{mention.user.screen_name}: {mention.full_text}")
        reply_text = generate_reply(mention.full_text)
        try:
            api.update_status(
                status=f"@{mention.user.screen_name} {reply_text}",
                in_reply_to_status_id=mention.id
            )
            print(f"✅ Replied to @{mention.user.screen_name}")
        except tweepy.TweepyException as e:
            print(f"❌ Failed to reply: {e}")

        since_id = max(since_id, mention.id)

    # ✅ Always write latest since_id
    with open("since_id.txt", "w") as f:
        f.write(str(since_id))

if __name__ == "__main__":
    reply_to_mentions()
