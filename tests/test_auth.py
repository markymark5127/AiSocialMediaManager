import os
import tweepy


def main():
    print("🔐 Testing Twitter API credentials...")

    auth = tweepy.OAuth1UserHandler(
        os.getenv("TWITTER_API_KEY"),
        os.getenv("TWITTER_API_SECRET"),
        os.getenv("TWITTER_ACCESS_TOKEN"),
        os.getenv("TWITTER_ACCESS_SECRET")
    )

    api = tweepy.API(auth)

    try:
        user = api.verify_credentials()
        if user:
            print(f"✅ Auth successful. Logged in as: @{user.screen_name}")
        else:
            print("❌ Auth failed. No user returned.")
    except Exception as e:
        print("❌ Auth exception:", e)


if __name__ == "__main__":
    main()
