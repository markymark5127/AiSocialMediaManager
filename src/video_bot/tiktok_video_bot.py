import os
import sys
import requests

sys.path.append(os.path.dirname(__file__))
from generate_video import generate_script, save_text_as_audio, generate_video

TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")


def query_creator_info(token: str):
    url = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    resp = requests.post(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def init_video_upload(token: str, title: str, video_size: int):
    url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    data = {
        "post_info": {
            "title": title[:150],
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "video_cover_timestamp_ms": 1000,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": video_size,
            "total_chunk_count": 1,
        },
    }
    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()


def upload_video_file(upload_url: str, video_path: str):
    size = os.path.getsize(video_path)
    headers = {
        "Content-Range": f"bytes 0-{size-1}/{size}",
        "Content-Type": "video/mp4",
    }
    with open(video_path, "rb") as f:
        resp = requests.put(upload_url, headers=headers, data=f)
    resp.raise_for_status()


def check_status(token: str, publish_id: str):
    url = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    resp = requests.post(url, headers=headers, json={"publish_id": publish_id})
    resp.raise_for_status()
    return resp.json()


def post_video_to_tiktok(video_path: str, title: str):
    token = TIKTOK_ACCESS_TOKEN
    if not token:
        print("TIKTOK_ACCESS_TOKEN not configured.")
        return

    query_creator_info(token)
    size = os.path.getsize(video_path)
    init_resp = init_video_upload(token, title, size)
    upload_url = init_resp["data"]["upload_url"]
    publish_id = init_resp["data"]["publish_id"]
    upload_video_file(upload_url, video_path)
    status = check_status(token, publish_id)
    print("TikTok upload status:", status)


if __name__ == "__main__":
    print("Generating video for TikTok...")
    script_text = generate_script()
    save_text_as_audio(script_text)
    generate_video(script_text)
    # post_video_to_tiktok("output_reel.mp4", script_text)
