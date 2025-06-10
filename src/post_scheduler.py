import os
import random
from datetime import datetime, timedelta

import openai
import requests
import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler

openai.api_key = os.getenv("OPENAI_API_KEY")

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


def generate_random_times(start_hour: int = 8, end_hour: int = 22, count: int = 3):
    """Return a list of datetime objects for today between start_hour and end_hour."""
    now = datetime.now()
    start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    if end <= start:
        end += timedelta(days=1)
    seconds_range = int((end - start).total_seconds())
    return [start + timedelta(seconds=random.randint(0, seconds_range)) for _ in range(count)]


def generate_ai_post(style: str, platform: str) -> str:
    prompts = {
        "funny": "Write a short, witty social media post about our AI app.",
        "serious": "Write a professional announcement about a new feature in our AI app.",
        "update": "Write a brief update on today's improvements to our AI app.",
    }
    prompt = prompts.get(style, prompts["update"])
    if platform == "twitter":
        prompt += " Limit to 280 characters."
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return response["choices"][0]["message"]["content"].strip()


def post_to_twitter(message: str):
    if not twitter_api:
        print("Twitter credentials not configured.")
        return
    twitter_api.update_status(status=message)


def post_to_facebook(message: str):
    if not (META_ACCESS_TOKEN and FB_PAGE_ID):
        print("Facebook credentials not configured.")
        return
    url = f"https://graph.facebook.com/v17.0/{FB_PAGE_ID}/feed"
    requests.post(url, data={"message": message, "access_token": META_ACCESS_TOKEN})


def post_to_instagram(message: str):
    if not (META_ACCESS_TOKEN and IG_USER_ID):
        print("Instagram credentials not configured.")
        return
    create_url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media"
    resp = requests.post(create_url, data={"caption": message, "access_token": META_ACCESS_TOKEN})
    creation_id = resp.json().get("id")
    if creation_id:
        publish_url = f"https://graph.facebook.com/v17.0/{IG_USER_ID}/media_publish"
        requests.post(publish_url, data={"creation_id": creation_id, "access_token": META_ACCESS_TOKEN})


def post_to_tiktok(message: str):
    print("TikTok posting not implemented. Message:", message)


def post_content(platform: str):
    style = random.choice(["funny", "serious", "update"])
    content = generate_ai_post(style, platform)

    if platform == "twitter":
        post_to_twitter(content)
    elif platform == "facebook":
        post_to_facebook(content)
    elif platform == "instagram":
        post_to_instagram(content)
    elif platform == "tiktok":
        post_to_tiktok(content)
    print(f"Posted on {platform} at {datetime.now().isoformat()} with style: {style}")


def schedule_daily_posts():
    scheduler = BlockingScheduler()
    platforms = ["twitter", "facebook", "instagram", "tiktok"]
    for platform in platforms:
        for run_time in generate_random_times():
            scheduler.add_job(post_content, "date", run_date=run_time, args=[platform])
            print(f"Scheduled {platform} post for {run_time}")
    scheduler.start()


if __name__ == "__main__":
    schedule_daily_posts()
