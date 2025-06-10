
import openai
import subprocess
import os
import random
from gtts import gTTS
from datetime import datetime

# Environment variable for OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
IMAGE_DIR = os.getenv("IMAGE_DIR", "images")

def generate_script():
    prompt = "Write a short 15-second video script promoting a free AI recipe app that generates meal ideas based on fridge photos. Make it friendly, use emojis, and end with a call to action."
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def get_random_background() -> str:
    if not os.path.isdir(IMAGE_DIR):
        return "background.jpg"
    imgs = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    return random.choice(imgs) if imgs else "background.jpg"

def save_text_as_audio(text, audio_path="voiceover.mp3"):
    tts = gTTS(text)
    tts.save(audio_path)
    print("🔊 Audio saved with gTTS.")

def save_subtitles(text, srt_path="captions.srt"):
    lines = text.split(". ")
    with open(srt_path, "w") as f:
        for i, line in enumerate(lines):
            start = f"00:00:{i*2:02},000"
            end = f"00:00:{(i+1)*2:02},000"
            f.write(f"{i+1}\n{start} --> {end}\n{line.strip()}\n\n")
    print("📝 Captions saved to captions.srt")

def generate_video(script_text, image_path="background.jpg", output_path="output_reel.mp4"):
    save_subtitles(script_text)

    command = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_path,
        "-i", "voiceover.mp3",
        "-vf", "scale=720:1280,subtitles=captions.srt",
        "-shortest",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path
    ]

    subprocess.run(command)
    print(f"✅ Video saved to {output_path}")

if __name__ == "__main__":
    print("🎬 Generating AI-powered promo video...")
    script = generate_script()
    print("📜 Script:\n", script)
    save_text_as_audio(script)
    bg = get_random_background()
    generate_video(script, image_path=bg)
