"""Example script that posts a daily tweet with an image using both
Tweepy API v1.1 and v2 clients.

The tweet text includes the number of days since November 6, 2023. After
posting, the image file is moved to an ``archives`` folder with the
current date as the filename.

Required environment variables:
    TWITTER_CONSUMER_KEY
    TWITTER_CONSUMER_SECRET
    TWITTER_ACCESS_TOKEN
    TWITTER_ACCESS_SECRET
    TWITTER_BEARER_TOKEN
"""

from __future__ import annotations

import os
import pathlib
import shutil
from datetime import date

import tweepy

START_DATE = date(2023, 11, 6)


def _find_png(directory: str) -> str | None:
    """Return the first ``.png`` file found in *directory*, if any."""
    for name in os.listdir(directory):
        if name.lower().endswith(".png"):
            return name
    return None


def main() -> None:
    days = (date.today() - START_DATE).days + 1
    tweet_text = (
        f"Day {days} of testing twitter:\n"
        "Why did the computer apply for a job at the bakery? \U0001F35E "
        "It wanted to work on its 'bread'ware skills! \U0001F602 #TechHumor "
        "#BakingBytes #ProgrammingPuns\n"
        "I wanted to test a tweet and if you are seeing this, I have "
        "successfully completed the post. Yay!"
    )

    consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")
    bearer = os.getenv("TWITTER_BEARER_TOKEN")

    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_secret
    )
    api_v1 = tweepy.API(auth)
    client_v2 = tweepy.Client(
        bearer_token=bearer,
        access_token=access_token,
        access_token_secret=access_secret,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
    )

    script_dir = os.path.abspath(os.path.dirname(__file__))
    image_name = _find_png(script_dir)

    media_id = None
    if image_name:
        upload = api_v1.media_upload(os.path.join(script_dir, image_name))
        media_id = upload.media_id

    result = client_v2.create_tweet(
        text=tweet_text, media_ids=[media_id] if media_id else None
    )
    print(result)

    if image_name:
        archive_dir = os.path.join(script_dir, "archives")
        os.makedirs(archive_dir, exist_ok=True)
        ext = pathlib.Path(image_name).suffix
        shutil.move(
            os.path.join(script_dir, image_name),
            os.path.join(archive_dir, date.today().strftime("%Y%m%d") + ext),
        )


if __name__ == "__main__":
    main()
