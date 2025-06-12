import os
import random
from datetime import datetime
from pathlib import Path

import requests
from openai import OpenAI

TOPIC_FILE = os.getenv("TOPIC_FILE", "topics.txt")
IMAGE_DIR = os.getenv("IMAGE_DIR", "images")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _load_topics() -> list[str]:
    if not os.path.exists(TOPIC_FILE):
        return ["our product"]
    with open(TOPIC_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]


def _get_random_topic() -> str:
    return random.choice(_load_topics())


def _random_style() -> str:
    return random.choice(["funny", "serious"])


def generate_post(topic: str, style: str) -> str:
    prompt = (
        f"Write a short {style} Facebook post about {topic}. "
        "Add a couple relevant hashtags at the end."
    )
    for i in range(3):
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
            )
            post = res.choices[0].message.content.strip()
            print(f"✅ Generated post (attempt {i+1}): {post}")
            return post
        except Exception as e:
            print(f"⚠️ GPT error (attempt {i+1}): {e}")
    raise RuntimeError("Failed to generate post after 3 attempts")


def generate_image_from_post(post: str) -> str | None:
    try:
        print("🖼️ Requesting image generation based on post text...")
        res = client.images.generate(
            model="dall-e-3",
            prompt=(
                f"Create an engaging image to visually represent this Facebook post: \"{post}\". "
                "It should match the theme and avoid text in the image."
            ),
            size="1024x1024",
            quality="standard",
            n=1,
        )
        url = res.data[0].url
        print(f"🎨 Generated image URL: {url}")
        return url
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        return None


def download_image(url: str) -> str | None:
    try:
        r = requests.get(url)
        path = os.path.join(IMAGE_DIR, "fb_temp.jpg")
        os.makedirs(IMAGE_DIR, exist_ok=True)
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"✅ Image saved to {path}")
        return path
    except Exception as e:
        print(f"❌ Failed to download image: {e}")
        return None


def post_to_facebook(text: str, image_path: str | None = None):
    token = os.getenv("META_ACCESS_TOKEN")
    page_id = os.getenv("FB_PAGE_ID")
    if not token or not page_id:
        print("❌ Facebook credentials not configured.")
        return

    if image_path and os.path.exists(image_path):
        url = f"https://graph.facebook.com/v17.0/{page_id}/photos"
        with open(image_path, "rb") as img:
            requests.post(
                url,
                data={"caption": text, "access_token": token},
                files={"source": img},
            )
    else:
        url = f"https://graph.facebook.com/v17.0/{page_id}/feed"
        requests.post(url, data={"message": text, "access_token": token})
    print("✅ Post sent to Facebook")


def main():
    style = _random_style()
    topic = _get_random_topic()
    post = generate_post(topic, style)
    image_url = generate_image_from_post(post)
    image_path = download_image(image_url) if image_url else None
    post_to_facebook(post, image_path)
    if image_path and os.path.exists(image_path):
        Path(image_path).unlink(missing_ok=True)
    print(f"[{datetime.now().isoformat()}] Posted to Facebook with style {style} about '{topic}'")


if __name__ == "__main__":
    main()
