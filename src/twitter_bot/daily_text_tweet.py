import os
import random
from datetime import datetime

import tweepy
from openai import OpenAI

TOPIC_FILE = os.getenv("TOPIC_FILE", "topics.txt")
STYLE_STATE_FILE = os.getenv("STYLE_STATE_FILE", "tweet_style.txt")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_SECRET"),
)
twitter_api = tweepy.API(auth)


def _load_topics():
    if not os.path.exists(TOPIC_FILE):
        return ["our product"]
    with open(TOPIC_FILE, "r") as f:
        topics = [line.strip() for line in f if line.strip()]
    return topics or ["our product"]


def _get_random_topic():
    return random.choice(_load_topics())


def _next_style() -> str:
    """Alternate between 'funny' and 'serious' styles."""
    last = None
    if os.path.exists(STYLE_STATE_FILE):
        with open(STYLE_STATE_FILE, "r") as f:
            last = f.read().strip()
    style = "serious" if last == "funny" else "funny"
    with open(STYLE_STATE_FILE, "w") as f:
        f.write(style)
    return style


def generate_tweet(topic: str, style: str) -> str:
    prompt = (
        f"Write a short {style} tweet about {topic}. "
        "Add a couple popular hashtags relevant to the topic."
    )
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content.strip()


def post_tweet(text: str):
    try:
        twitter_api.update_status(status=text)
    except tweepy.errors.TweepyException as exc:
        print(f"Failed to post tweet: {exc}")


def main():
    style = _next_style()
    topic = _get_random_topic()
    tweet = generate_tweet(topic, style)
    post_tweet(tweet)
    print(f"[{datetime.now().isoformat()}] Tweeted with style {style} about '{topic}'")


if __name__ == "__main__":
    main()
