"""Simple engagement automation for Twitter.

- Auto-follow users who mention or reply to you.
- Like a recent post from each follower to boost retention.
- Unfollow accounts that don't follow back after a configurable
  number of days.

This script stores follow timestamps in ``followed.json``.
Use responsibly and stay within the platform's rate limits.
"""

import json
import os
import time
from datetime import datetime, timedelta

import tweepy

FOLLOW_FILE = "followed.json"
UNFOLLOW_AFTER_DAYS = int(os.getenv("UNFOLLOW_AFTER_DAYS", "7"))

auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_SECRET"),
)
api = tweepy.API(auth)


def load_followed():
    if os.path.exists(FOLLOW_FILE):
        with open(FOLLOW_FILE) as f:
            return json.load(f)
    return {}


def save_followed(data):
    with open(FOLLOW_FILE, "w") as f:
        json.dump(data, f)


def follow_engagers():
    """Follow users who recently engaged with mentions."""
    followed = load_followed()
    mentions = api.mentions_timeline(count=20)
    for m in mentions:
        uid = str(m.user.id)
        if uid not in followed:
            api.create_friendship(uid)
            followed[uid] = datetime.utcnow().isoformat()
            print("Followed", m.user.screen_name)
    save_followed(followed)


def like_recent_posts():
    """Like the most recent tweet from each follower."""
    for follower in tweepy.Cursor(api.followers).items(20):
        tweets = api.user_timeline(user_id=follower.id, count=1)
        for t in tweets:
            try:
                api.create_favorite(t.id)
                print("Liked tweet from", follower.screen_name)
            except tweepy.TweepError:
                pass


def unfollow_nonfollowers():
    """Unfollow accounts that haven't followed back after N days."""
    followed = load_followed()
    followers_ids = set(str(fid) for fid in api.followers_ids())
    cutoff = datetime.utcnow() - timedelta(days=UNFOLLOW_AFTER_DAYS)
    updated = False
    for uid, ts in list(followed.items()):
        if uid not in followers_ids and datetime.fromisoformat(ts) < cutoff:
            api.destroy_friendship(uid)
            print("Unfollowed", uid)
            del followed[uid]
            updated = True
    if updated:
        save_followed(followed)


if __name__ == "__main__":
    follow_engagers()
    like_recent_posts()
    unfollow_nonfollowers()
