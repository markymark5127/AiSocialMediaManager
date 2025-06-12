import os
import random
from pathlib import Path
from datetime import datetime

import requests
import tweepy
from openai import OpenAI

# Setup
TOPIC_FILE = os.getenv("TOPIC_FILE", "topics.txt")
IMAGE_DIR = os.getenv("IMAGE_DIR", "images")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Twitter Auth
def _create_twitter_clients() -> tuple[tweepy.API, tweepy.Client]:
    auth = tweepy.OAuth1UserHandler(
        os.getenv("TWITTER_API_KEY"),
        os.getenv("TWITTER_API_SECRET"),
        os.getenv("TWITTER_ACCESS_TOKEN"),
        os.getenv("TWITTER_ACCESS_SECRET"),
    )
    api_v1 = tweepy.API(auth)
    client_v2 = tweepy.Client(
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
    )
    return api_v1, client_v2

twitter_api_v1, twitter_client_v2 = _create_twitter_clients()

# Topic & Style
def _load_topics():
    if not os.path.exists(TOPIC_FILE):
        return ["our product"]
    with open(TOPIC_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def _get_random_topic():
    return random.choice(_load_topics())

def _random_style():
    return random.choice(["funny", "serious"])

# Tweet Generation
def generate_tweet(topic: str, style: str) -> str:
    prompt = (
        f"Write a short {style} tweet about {topic}. "
        "Add a couple relevant hashtags at the end."
    )
    for i in range(3):  # Retry in case of API hiccups
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
            )
            tweet = res.choices[0].message.content.strip()
            print(f"✅ Generated tweet (attempt {i+1}): {tweet}")
            return tweet
        except Exception as e:
            print(f"⚠️ GPT error (attempt {i+1}): {e}")
    raise RuntimeError("Failed to generate tweet after 3 attempts")

# Image Generation from Tweet Content
def generate_image_from_tweet(tweet: str) -> str | None:
    try:
        print("🖼️ Requesting image generation based on tweet text...")
        res = client.images.generate(
            model="dall-e-3",
            prompt=f"Create an engaging image to visually represent this tweet: \"{tweet}\". It should match the theme and include visual metaphor where appropriate. Avoid text in the image.",
            size="1024x1024",
            quality="standard",
            n=1
        )
        url = res.data[0].url
        print(f"🎨 Generated image URL: {url}")
        return url
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        return None

# Download image
def download_image(url: str) -> str | None:
    try:
        r = requests.get(url)
        path = os.path.join(IMAGE_DIR, "tweet_temp.jpg")
        os.makedirs(IMAGE_DIR, exist_ok=True)
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"✅ Image saved to {path}")
        return path
    except Exception as e:
        print(f"❌ Failed to download image: {e}")
        return None

# Post Tweet
def post_tweet(text: str, image_path: str | None = None):
    media_ids = []
    if image_path and os.path.exists(image_path):
        try:
            print(f"📤 Uploading image via v1.1: {image_path}")
            media = twitter_api_v1.media_upload(image_path)
            media_ids = [media.media_id]
        except Exception as e:
            print(f"❌ Failed to upload media: {e}")
    try:
        print(f"📢 Posting tweet via v2 with media_ids: {media_ids}")
        twitter_client_v2.create_tweet(
            text=text,
            media_ids=media_ids if media_ids else None
        )
        print("✅ Tweet posted successfully!")
    except tweepy.TweepyException as e:
        print(f"❌ Failed to post tweet: {e}")

# Main Bot
def main():
    style = _random_style()
    topic = _get_random_topic()
    tweet = generate_tweet(topic, style)
    image_url = generate_image_from_tweet(tweet)
    image_path = download_image(image_url) if image_url else None
    post_tweet(tweet, image_path)
    if image_path and os.path.exists(image_path):
        os.remove(image_path)
    print(f"[{datetime.now().isoformat()}] Tweeted with style {style} about '{topic}'")

if __name__ == "__main__":
    main()
