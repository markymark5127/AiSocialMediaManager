
# Instagram comment reply automation requires:
# - Facebook App
# - Instagram Business Account linked to a Facebook Page
# - Access tokens with 'instagram_manage_comments' and 'pages_show_list' permissions

# Use requests to hit the Meta Graph API:
# 1. GET /{ig-media-id}/comments
# 2. POST /{comment-id}/replies

import requests
import os

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
IG_BUSINESS_ID = os.getenv("IG_BUSINESS_ID")

def get_comments(media_id):
    url = f"https://graph.facebook.com/v17.0/{media_id}/comments?access_token={ACCESS_TOKEN}"
    return requests.get(url).json()

def reply_to_comment(comment_id, message):
    url = f"https://graph.facebook.com/v17.0/{comment_id}/replies"
    data = {"message": message, "access_token": ACCESS_TOKEN}
    return requests.post(url, data=data).json()

# Example usage:
# comments = get_comments("MEDIA_ID_HERE")
# for c in comments['data']:
#     reply_to_comment(c['id'], "Thanks for the comment! Check out the app here: [link]")
