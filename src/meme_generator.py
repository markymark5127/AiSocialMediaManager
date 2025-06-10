"""Generate trending AI memes and convert them into short videos."""
import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import openai
from src.video_bot.generate_video import generate_video

openai.api_key = os.getenv("OPENAI_API_KEY")

HEADERS = {"User-Agent": "meme-generator"}


def get_trending_meme_title() -> str:
    """Return the title of a trending meme from Reddit."""
    url = "https://www.reddit.com/r/aiMemes/top.json?limit=5&t=day"
    r = requests.get(url, headers=HEADERS)
    if r.ok:
        posts = r.json().get("data", {}).get("children", [])
        if posts:
            return posts[0]["data"].get("title", "AI meme")
    return "AI meme"


def generate_image(prompt: str) -> bytes:
    """Use OpenAI to create an image for the meme."""
    resp = openai.Image.create(prompt=prompt, n=1, size="512x512")
    img_url = resp["data"][0]["url"]
    return requests.get(img_url).content


def caption_image(img_bytes: bytes, caption: str, out_path: str = "meme.png") -> str:
    img = Image.open(BytesIO(img_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except IOError:
        font = ImageFont.load_default()
    draw.text((10, 10), caption, fill="white", font=font)
    img.save(out_path)
    return out_path


def create_meme_video():
    trend = get_trending_meme_title()
    caption_resp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"Write a witty short caption about {trend}"}],
    )
    caption = caption_resp["choices"][0]["message"]["content"].strip()
    img_bytes = generate_image(trend)
    image_path = caption_image(img_bytes, caption)
    generate_video(caption, image_path=image_path, output_path="meme_video.mp4")
    print("Created meme video meme_video.mp4")


if __name__ == "__main__":
    create_meme_video()
