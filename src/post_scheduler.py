import os
import random
import smtplib
import traceback
from datetime import datetime, timedelta
from email.mime.text import MIMEText

import openai
import requests
import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler

openai.api_key = os.getenv("OPENAI_API_KEY")
TOPIC_FILE = os.getenv("TOPIC_FILE", "topics.txt")
IMAGE_DIR = os.getenv("IMAGE_DIR", "images")
LOG_FILE = os.getenv("LOG_FILE", "log.txt")


def log(message: str):
    """Append a timestamped message to LOG_FILE."""
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} {message}\n")

# Twitter authentication
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

if all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
    _tw_auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_SECRET,
    )
    twitter_api = tweepy.API(_tw_auth)
else:
    twitter_api = None

# Meta credentials for Facebook and Instagram
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID") or os.getenv("IG_BUSINESS_ID")
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")

# Email settings for error alerts
ERROR_EMAIL = os.getenv("ERROR_EMAIL")
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 25))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_error_email(subject: str, body: str):
    if not ERROR_EMAIL:
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER or ERROR_EMAIL
    msg["To"] = ERROR_EMAIL
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            if EMAIL_USER and EMAIL_PASSWORD:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(msg["From"], [ERROR_EMAIL], msg.as_string())
    except Exception as exc:
        print("Failed to send error email:", exc)


def twitter_authenticated() -> bool:
    if not twitter_api:
        return False
    try:
        twitter_api.verify_credentials()
        return True
    except Exception as exc:
        print("Twitter auth failed:", exc)
        return False


def facebook_authenticated() -> bool:
    if not (META_ACCESS_TOKEN and FB_PAGE_ID):
        return False
    try:
        resp = requests.get(
            f"https://graph.facebook.com/v17.0/me?access_token={META_ACCESS_TOKEN}"
        )
        return resp.status_code == 200
    except Exception as exc:
        print("Facebook auth failed:", exc)
        return False


def instagram_authenticated() -> bool:
    if not (META_ACCESS_TOKEN and IG_USER_ID):
        return False
    try:
        resp = requests.get(
            f"https://graph.facebook.com/v17.0/{IG_USER_ID}?fields=id&access_token={META_ACCESS_TOKEN}"
        )
        return resp.status_code == 200
    except Exception as exc:
        print("Instagram auth failed:", exc)
        return False


def tiktok_authenticated() -> bool:
    if not TIKTOK_ACCESS_TOKEN:
        return False
    try:
        from video_bot.tiktok_video_bot import query_creator_info

        query_creator_info(TIKTOK_ACCESS_TOKEN)
        return True
    except Exception as exc:
        print("TikTok auth failed:", exc)
        return False


def _random_times_between(start: datetime, end: datetime, count: int) -> list[datetime]:
    """Helper to pick `count` random datetimes between start and end."""
    seconds_range = int((end - start).total_seconds())
    if count > seconds_range:
        count = seconds_range
    seconds = random.sample(range(seconds_range), count)
    return [start + timedelta(seconds=s) for s in seconds]


def generate_random_times(start_hour: int = 8, end_hour: int = 22, count: int = 3) -> list[datetime]:
    """Return random future times today or tomorrow between start_hour and end_hour."""
    now = datetime.now()

    start_today = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end_today = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    if end_today <= start_today:
        end_today += timedelta(days=1)

    times = []

    # Times remaining today that are still in the future
    if now < end_today:
        start = max(start_today, now + timedelta(minutes=1))
        times.extend(t for t in _random_times_between(start, end_today, count) if t > now)

    # If not enough times left today, schedule the rest for tomorrow
    if len(times) < count:
        tomorrow = now + timedelta(days=1)
        start_tomorrow = tomorrow.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_tomorrow = tomorrow.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        if end_tomorrow <= start_tomorrow:
            end_tomorrow += timedelta(days=1)
        remaining = count - len(times)
        times.extend(_random_times_between(start_tomorrow, end_tomorrow, remaining))

    return sorted(times[:count])


def get_random_topic() -> str:
    if not os.path.exists(TOPIC_FILE):
        return "our AI app"
    with open(TOPIC_FILE, "r") as f:
        topics = [line.strip() for line in f if line.strip()]
    return random.choice(topics) if topics else "our AI app"


def get_seed_image() -> str | None:
    if not os.path.isdir(IMAGE_DIR):
        return None
    imgs = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    return random.choice(imgs) if imgs else None


def generate_image(seed_image: str | None) -> str | None:
    if not seed_image:
        return None
    try:
        with open(seed_image, "rb") as img:
            resp = openai.Image.create_variation(image=img, n=1, size="1024x1024")
        return resp["data"][0]["url"]
    except Exception as exc:
        print("Image generation failed:", exc)
        return None


def generate_ai_post(topic: str, style: str, platform: str) -> str:
    prompt = f"Write a {style} social media post about {topic}."
    if platform == "twitter":
        prompt += " Limit to 280 characters."
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return response["choices"][0]["message"]["content"].strip()


def post_to_twitter(message: str, image_path: str | None = None):
    if not twitter_authenticated():
        return
    if image_path:
        media = twitter_api.media_upload(image_path)
        twitter_api.update_status(status=message, media_ids=[media.media_id])
    else:
        twitter_api.update_status(status=message)
    log("Posted to twitter")


def post_to_facebook(message: str, image_url: str | None = None, image_path: str | None = None):
    if not facebook_authenticated():
        return
    if image_path:
        url = f"https://graph.facebook.com/v17.0/{FB_PAGE_ID}/photos"
        with open(image_path, "rb") as img:
            requests.post(url, data={"caption": message, "access_token": META_ACCESS_TOKEN}, files={"source": img})
    elif image_url:
        url = f"https://graph.facebook.com/v17.0/{FB_PAGE_ID}/photos"
        requests.post(url, data={"caption": message, "url": image_url, "access_token": META_ACCESS_TOKEN})
    else:
        url = f"https://graph.facebook.com/v17.0/{FB_PAGE_ID}/feed"
        requests.post(url, data={"message": message, "access_token": META_ACCESS_TOKEN})
    log("Posted to facebook")


def post_to_instagram(message: str, image_url: str | None = None):
    if not instagram_authenticated():
        return
    create_url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media"
    payload = {"caption": message, "access_token": META_ACCESS_TOKEN}
    if image_url:
        payload["image_url"] = image_url
    resp = requests.post(create_url, data=payload)
    creation_id = resp.json().get("id")
    if creation_id:
        publish_url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media_publish"
        requests.post(publish_url, data={"creation_id": creation_id, "access_token": META_ACCESS_TOKEN})
    log("Posted to instagram")


def post_to_tiktok(message: str):
    if not tiktok_authenticated():
        return
    try:
        from video_bot.generate_video import generate_script, save_text_as_audio, generate_video, get_random_background
        from video_bot.tiktok_video_bot import post_video_to_tiktok
    except Exception as exc:
        print("TikTok modules not available:", exc)
        return
    script = generate_script()
    save_text_as_audio(script)
    bg = get_random_background()
    generate_video(script, image_path=bg)
    post_video_to_tiktok("output_reel.mp4", message)
    log("Posted to tiktok")


def post_content(platform: str):
    try:
        if platform == "twitter" and not twitter_authenticated():
            log("Skipped twitter due to auth failure")
            return
        if platform == "facebook" and not facebook_authenticated():
            log("Skipped facebook due to auth failure")
            return
        if platform == "instagram" and not instagram_authenticated():
            log("Skipped instagram due to auth failure")
            return
        if platform == "tiktok" and not tiktok_authenticated():
            log("Skipped tiktok due to auth failure")
            return
        style = random.choice(["funny", "serious", "update"])
        topic = get_random_topic()
        content = generate_ai_post(topic, style, platform)
        seed_image = get_seed_image() if platform in {"facebook", "instagram", "twitter"} else None
        image_url = generate_image(seed_image) if seed_image else None

        if platform == "twitter":
            img_path = None
            if image_url and image_url.startswith("http"):
                try:
                    img_path = os.path.join(IMAGE_DIR, "tw_dl.jpg")
                    r = requests.get(image_url)
                    with open(img_path, "wb") as f:
                        f.write(r.content)
                except Exception:
                    img_path = None
            post_to_twitter(content, img_path)
        elif platform == "facebook":
            post_to_facebook(content, image_url=image_url)
        elif platform == "instagram":
            post_to_instagram(content, image_url=image_url)
        elif platform == "tiktok":
            post_to_tiktok(content)
        print(
            f"Posted on {platform} at {datetime.now().isoformat()} with style: {style} topic: {topic}"
        )
    except Exception as exc:
        err = traceback.format_exc()
        send_error_email(f"Post to {platform} failed", err)
        print(f"Failed to post on {platform}:", exc)


def schedule_daily_posts():
    scheduler = BlockingScheduler()
    platforms = ["twitter", "facebook", "instagram", "tiktok"]
    for platform in platforms:
        for run_time in generate_random_times():
            scheduler.add_job(post_content, "date", run_date=run_time, args=[platform])
            print(f"Scheduled {platform} post for {run_time}")
    try:
        scheduler.start()
    except Exception:
        err = traceback.format_exc()
        send_error_email("Scheduler failed", err)
        print("Scheduler failed:", err)


if __name__ == "__main__":
    schedule_daily_posts()
