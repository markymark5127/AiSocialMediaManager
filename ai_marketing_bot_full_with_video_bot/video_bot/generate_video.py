
import openai
import subprocess
import os
from datetime import datetime

# Environment variable for OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_script():
    prompt = "Write a short 15-second video script promoting a free AI recipe app that generates meal ideas based on fridge photos. Make it friendly, use emojis, and end with a call to action."
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def save_text_as_audio(text, audio_path="voiceover.mp3"):
    # Placeholder for TTS — use your preferred TTS engine here
    # For example: gTTS, Tortoise TTS, or a pre-recorded clip
    with open(audio_path, "wb") as f:
        f.write(b"")  # Replace with actual TTS output
    print("⚠️ Dummy audio file created. Replace with real TTS output.")

def generate_video(script_text, image_path="background.jpg", output_path="output_reel.mp4"):
    # Save the script to overlay as text later
    with open("script.txt", "w") as f:
        f.write(script_text)

    # FFmpeg command to create a vertical video from an image + dummy audio
    command = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_path,
        "-i", "voiceover.mp3",
        "-shortest",
        "-vf", "scale=720:1280,format=yuv420p",
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
    print("📜 Script:
", script)
    save_text_as_audio(script)
    generate_video(script)
