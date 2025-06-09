# AI Social Media Manager

This repository contains a lightweight collection of scripts that automate basic social media marketing tasks.  The project grew out of several experiments which are now consolidated into a single `src` folder.

## Features

* **Twitter/X Auto‑Responder** – replies to recent mentions every six hours using OpenAI to craft a helpful response.
* **AI Video Generator** – creates a short vertical video with voiceover and captions that can be posted to Reels/TikTok.
* **Instagram Comment Reply (stub)** – demonstrates how a reply endpoint could be implemented using the Meta Graph API.

The automation is designed to run on free tiers such as GitHub Actions.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the following environment variables for the APIs you intend to use:
   - `OPENAI_API_KEY`
   - `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET`
   - `META_ACCESS_TOKEN`, `IG_BUSINESS_ID` (optional for Instagram)
3. Run the individual scripts from the `src` directory.  For example:
   ```bash
   python src/twitter_bot/reply_mentions.py
   ```

The GitHub Actions workflow in `.github/workflows/reply_bot.yml` is configured to run the Twitter bot every six hours.

## Repository Layout

```
src/
  twitter_bot/reply_mentions.py   # Twitter/X reply automation
  video_bot/generate_video.py     # AI‑generated vertical video
  instagram_bot/instagram_replies.py  # Meta API scaffold
```

The repository retains the MIT license.
