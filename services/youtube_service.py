import yt_dlp
import os
import re


def sanitize_filename(name: str) -> str:
    """
    Make filename safe for all OSes.
    """
    name = name.lower().strip()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_-]+", "_", name)
    return name


def download_youtube_video(video_id, output_dir):
    url = f"https://www.youtube.com/watch?v={video_id}"

    # First extract info WITHOUT downloading
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    title = info.get("title", video_id)
    safe_title = sanitize_filename(title)

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(output_dir, f"{safe_title}.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    media_path = os.path.join(output_dir, f"{safe_title}.mp4")

    return media_path, title


def download_youtube_audio():
    pass
