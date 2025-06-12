# AI Social Media Manager

This repository contains a lightweight collection of scripts that automate basic social media marketing tasks.  The project grew out of several experiments which are now consolidated into a single `src` folder.

## Features

* **Twitter/X Auto‑Responder** – replies to recent mentions every six hours using OpenAI to craft a helpful response.
* **AI Video Generator** – creates a short vertical video with voiceover and captions that can be posted to Reels/TikTok.
* **Instagram & Facebook Replies** – example code for responding to comments via the Meta Graph API.
* **Context‑Aware Auto‑Replies** – comment and DM responses include FAQ links and ignore spam keywords.
* **Follow/Unfollow & Engagement Bot** – automatically follow engagers, like follower posts, and unfollow nonfollowers after a set period.
* **Meme + Video Generator** – turns trending AI meme formats into short captioned videos.
* **Multi‑Platform Scheduler** – generates AI posts for Twitter, Facebook, Instagram, and TikTok when triggered.
* **Topic & Image Sources** – place text prompts in `topics.txt` and seed images in the `images/` folder. One topic and image are selected at random for each post.
* **Daily Twitter Bot** – once a day generates a tweet with hashtags and an AI image using a random topic and seed picture.
* **Text‑Only Tweet Bot** – variant that posts a short tweet with relevant hashtags but no image.
* **Daily Facebook Bot** – once a day posts an AI-generated Facebook update with an optional image.

The automation is designed to run on free tiers such as GitHub Actions.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the following environment variables for the APIs you intend to use:
   - `OPENAI_API_KEY`
   - `TWITTER_API_KEY` / `TWITTER_CONSUMER_KEY`
   - `TWITTER_API_SECRET` / `TWITTER_CONSUMER_SECRET`
   - `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET`, `TWITTER_BEARER_TOKEN`
   - `META_ACCESS_TOKEN`, `IG_BUSINESS_ID` (optional for Instagram)
3. Run the auth test script to verify your Twitter credentials:
   ```bash
   python tests/test_auth.py
   ```
4. Edit `topics.txt` with lines of text describing the content you want posted.
   Add seed images to the `images/` directory to influence the generated art.
5. Run the individual scripts from the `src` directory.  For example:
   ```bash
   python src/twitter_bot/reply_mentions.py
   ```

GitHub Actions workflows in `.github/workflows/` run the bots on a schedule. `social_media.yml` runs every eight hours and posts content to each platform.

## Repository Layout

```
src/
  twitter_bot/reply_mentions.py   # Twitter/X reply automation
  video_bot/generate_video.py     # AI‑generated vertical video
  instagram_bot/instagram_replies.py  # Meta API scaffold
  facebook_bot/reply_comments.py   # Facebook comment replies
  post_scheduler.py               # Immediate multi-platform posting
  engagement_bot.py               # Follow/unfollow automation
  meme_generator.py               # Trending meme video creator
  twitter_bot/daily_tweet.py      # Posts one AI-generated tweet per day
  facebook_bot/daily_facebook_post.py # Posts one AI-generated Facebook update per day
  twitter_bot/daily_text_tweet.py # Text-only version of the daily tweet bot
  twitter_bot/example_daily_tweet.py # Sample dual API image tweet script
```

The repository retains the MIT license.
