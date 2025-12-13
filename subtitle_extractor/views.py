from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from services.subtitle_service import extract_subtitles
from services.youtube_service import download_youtube_video
import os


def subtitle_extractor_view(request):
    context = {}

    if request.method == "POST":
        model = request.POST.get("model", "base")
        fmt = request.POST.get("format")
        yt_id = request.POST.get("youtube_id")

        fs = FileSystemStorage()

        subtitle_urls = {}
        subtitle_texts = {}

        # ================== STEP 1: GET MEDIA ==================
        if yt_id:
            media_path, title = download_youtube_video(yt_id, fs.location)
            media_url = fs.url(os.path.basename(media_path))
            is_youtube = True

            context["title"] = title
            context["youtube_id"] = yt_id

        elif request.FILES.get("media"):
            media = request.FILES["media"]
            media_name = fs.save(media.name, media)
            media_path = fs.path(media_name)
            media_url = fs.url(media_name)
            is_youtube = False

        else:
            # Safety fallback (frontend already validates)
            context["error"] = "No media provided"
            return render(request, "subtitle_extractor/extractor.html", context)

        # ================== STEP 2: EXTRACT SUBTITLES ==================
        if fmt == "srt_txt":
            srt_path = extract_subtitles(media_path, "srt", model)
            txt_path = extract_subtitles(media_path, "txt", model)

            subtitle_urls["srt"] = fs.url(os.path.basename(srt_path))
            subtitle_urls["txt"] = fs.url(os.path.basename(txt_path))

            subtitle_texts["srt"] = open(srt_path, encoding="utf-8").read()
            subtitle_texts["txt"] = open(txt_path, encoding="utf-8").read()

            multi_format = True

        else:
            subtitle_path = extract_subtitles(media_path, fmt, model)

            subtitle_urls[fmt] = fs.url(os.path.basename(subtitle_path))
            subtitle_texts[fmt] = open(subtitle_path, encoding="utf-8").read()

            multi_format = False

        # ================== STEP 3: CONTEXT ==================
        context.update({
            "media_url": media_url,
            "subtitle_urls": subtitle_urls,
            "subtitle_texts": subtitle_texts,
            "multi_format": multi_format,
            "is_youtube": is_youtube,
        })

    return render(request, "subtitle_extractor/extractor.html", context)
