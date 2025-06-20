import time
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_GET

import yt_dlp
import os



@csrf_exempt
def download_media(request):
    if request.method == "POST":
        url = request.POST.get("media_url")
        media_type = request.POST.get("format")

        if not url or not media_type:
            return JsonResponse({
                "status": "error",
                "message": "Missing URL or media type."
            }, status=400)

        output_dir = os.path.join("media", "downloads")
        os.makedirs(output_dir, exist_ok=True)

        outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")

        if media_type == "video-mp4":
            ydl_opts = {
                "format": '270+bestaudio/best[ext=mp4]',
                "outtmpl": outtmpl,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }]
            }
        elif media_type == "audio-mp3":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }],
            }
        else:
            return JsonResponse({
                "status": "error",
                "message": "Invalid media type."
            }, status=400)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if media_type == "audio-mp3":
                    filename = os.path.splitext(filename)[0] + ".mp3"

                return JsonResponse({
                    "status": "success",
                    "message": "Download successful!",
                    "filename": os.path.basename(filename),
                    "filepath": filename,
                })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Download failed: {str(e)}"
            }, status=500)

    return render(request, "media_downloader/downloader.html")
