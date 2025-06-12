import os
import random
from pathlib import Path
from datetime import datetime

import requests
import tweepy
from openai import OpenAI

# Environment-based config
TOPIC_FILE = os.getenv("TOPIC_FILE", "topics.txt")
IMAGE_DIR = os.getenv("IMAGE_DIR", "images")
STYLE_STATE_FILE = os.getenv("STYLE_STATE_FILE", "tweet_style.txt")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Twitter v1.1 client (OAuth 1.0a)
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


def _get_random_image():
    if not os.path.isdir(IMAGE_DIR):
        return None
    images = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR)
              if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    return random.choice(images) if images else None


def _next_style() -> str:
    """Randomly choose between 'funny' and 'serious' styles."""
    return random.choice(["funny", "serious"])



def generate_tweet(topic: str, style: str) -> str:
    prompt = (
        f"Write a {style} tweet about {topic}. "
        "Include a couple relevant hashtags at the end."
    )
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content.strip()


def generate_image(seed_image: str | None, topic: str) -> str | None:
    if not seed_image:
        return None
    try:
        response = client.images.create_variation(
            image=Path(seed_image),
            n=1,
            size="1024x1024"
        )
        return response.data[0].url
    except Exception as exc:
        print("Image generation failed:", exc)
        return None


def post_tweet(text: str, image_path: str | None = None):
    """Post a tweet with optional image using v1.1 API (free-tier safe)."""
    media_id = None
    if image_path and os.path.exists(image_path):
        try:
            if os.path.getsize(image_path) == 0:
                raise Exception("Image file is empty.")
            print(f"📤 Uploading image: {image_path}")
            media = twitter_api.media_upload(image_path)
            media_id = media.media_id
        except Exception as exc:
            print(f"❌ Failed to upload media: {exc}")
            media_id = None  # fallback to text-only

    try:
        twitter_api.update_status(status=text, media_ids=[media_id] if media_id else None)
        print("✅ Tweet posted successfully!")
    except tweepy.TweepyException as exc:
        print(f"❌ Failed to post tweet: {exc}")



def main():
    style = _next_style()
    topic = _get_random_topic()
    seed_image = _get_random_image()
    tweet = generate_tweet(topic, style)
    generated_url = generate_image(seed_image, topic)

    download_path = None
    if generated_url and generated_url.startswith("http"):
        try:
            r = requests.get(generated_url)
            download_path = os.path.join(IMAGE_DIR, "tweet_temp.jpg")
            with open(download_path, "wb") as f:
                f.write(r.content)
        except Exception as exc:
            print("Failed to download generated image:", exc)
            download_path = None

    post_tweet(tweet, download_path)

    # Cleanup temp image
    if download_path and os.path.exists(download_path):
        os.remove(download_path)

    print(f"[{datetime.now().isoformat()}] Tweeted with style {style} about '{topic}'")


if __name__ == "__main__":
    main()
