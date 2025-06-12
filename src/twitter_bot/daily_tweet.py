import os
import random
import time
from pathlib import Path
from datetime import datetime

import requests
import tweepy
from openai import OpenAI

# Configuration
TOPIC_FILE = os.getenv("TOPIC_FILE", "topics.txt")
IMAGE_DIR = os.getenv("IMAGE_DIR", "images")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Twitter API clients
twitter_api_v1 = tweepy.API(tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_SECRET"),
))

twitter_client_v2 = tweepy.Client(
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
)


def _load_topics():
    if not os.path.exists(TOPIC_FILE):
        return ["our product"]
    with open(TOPIC_FILE, "r") as f:
        topics = [line.strip() for line in f if line.strip()]
    return topics or ["our product"]


def _get_random_topic():
    return random.choice(_load_topics())


def _get_random_image():
    if not os.path.isdir(IMAGE_DIR):
        return None
    images = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR)
              if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    return random.choice(images) if images else None


def _next_style() -> str:
    return random.choice(["funny", "serious"])


def generate_tweet(topic: str, style: str, retries: int = 3, delay: float = 2.0) -> str:
    prompt = (
        f"Write a {style} tweet about {topic}. "
        "Include a couple relevant hashtags at the end."
    )
    for attempt in range(1, retries + 1):
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
            )
            content = res.choices[0].message.content.strip()
            if content:
                print(f"✅ Generated tweet (attempt {attempt}): {content}")
                return content
            else:
                raise ValueError("Empty tweet content.")
        except Exception as e:
            print(f"⚠️ GPT error (attempt {attempt}): {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                raise RuntimeError("❌ Failed to generate tweet after retries.")


def generate_image(seed_image: str | None, topic: str) -> str | None:
    if not seed_image or not os.path.exists(seed_image):
        print("⚠️ No valid seed image.")
        return None
    try:
        response = client.images.create_variation(
            image=Path(seed_image),
            n=1,
            size="1024x1024"
        )
        url = response.data[0].url if response.data else None
        print("🎨 Generated image URL:", url)
        return url
    except Exception as exc:
        print("❌ Image generation failed:", exc)
        return None


def download_image_safely(url: str, output_path: str) -> str | None:
    if not url or not url.startswith("http"):
        print("⚠️ Invalid image URL.")
        return None
    try:
        r = requests.get(url)
        if r.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(r.content)
            print(f"✅ Image saved to {output_path}")
            return output_path
        else:
            print(f"❌ Download failed. Status: {r.status_code}")
            return None
    except Exception as exc:
        print("❌ Download error:", exc)
        return None


def post_tweet(text: str, image_path: str | None = None):
    """Uploads media via v1.1, posts tweet via v2 (Free Tier safe)."""
    media_ids = []

    if image_path and os.path.exists(image_path):
        try:
            if os.path.getsize(image_path) == 0:
                raise Exception("Image is empty.")
            print(f"📤 Uploading image via v1.1: {image_path}")
            media = twitter_api_v1.media_upload(image_path)
            media_ids = [media.media_id]
        except Exception as exc:
            print(f"❌ Failed to upload media: {exc}")
            media_ids = []

    try:
        print(f"📢 Posting tweet via v2 with media_ids: {media_ids}")
        twitter_client_v2.create_tweet(
            text=text,
            media={"media_ids": media_ids} if media_ids else None
        )
        print("✅ Tweet posted successfully!")
    except tweepy.TweepyException as exc:
        print(f"❌ Failed to post tweet: {exc}")


def main():
    style = _next_style()
    topic = _get_random_topic()
    tweet = generate_tweet(topic, style)

    seed_image = _get_random_image()
    generated_url = generate_image(seed_image, topic)
    download_path = download_image_safely(generated_url, os.path.join(IMAGE_DIR, "tweet_temp.jpg")) if generated_url else None

    post_tweet(tweet, download_path)

    if download_path and os.path.exists(download_path):
        os.remove(download_path)

    print(f"[{datetime.now().isoformat()}] Tweeted with style '{style}' about '{topic}'")


if __name__ == "__main__":
    main()
