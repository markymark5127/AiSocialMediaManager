
from fastapi import FastAPI
from pydantic import BaseModel
import openai
import tweepy
import os

app = FastAPI()

# Load API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

class PostRequest(BaseModel):
    platform: str = "twitter"

@app.post("/run-marketing-bot")
async def run_bot(req: PostRequest):
    # Generate text using OpenAI
    prompt = "Write a tweet promoting an AI app that generates recipes from photos of your fridge."
    completion = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    tweet = completion.choices[0].message.content.strip()

    # Post to Twitter
    auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    api = tweepy.API(auth)
    api.update_status(status=tweet)

    return {"status": "success", "tweet": tweet}
