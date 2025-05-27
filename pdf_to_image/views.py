from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings

import os
import sys
from PIL import Image
from pdf2image import convert_from_path

venv_path = sys.prefix


def pdf_to_vertical_image(pdf_path, output_image_path, dpi=200):
    poppler_path = os.path.join(venv_path, "Poppler", "Library", "bin")
    pages = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)

    widths, heights = zip(*(page.size for page in pages))
    total_height = sum(heights)
    max_width = max(widths)
    result = Image.new('RGB', (max_width, total_height), color=(255, 255, 255))

    y_offset = 0
    for page in pages:
        result.paste(page, (0, y_offset))
        y_offset += page.size[1]

    result.save(output_image_path)


def upload_pdf(request):
    image_url = None
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]
        pdf_path = default_storage.save(f"pdfs/{pdf_file.name}", pdf_file)

        abs_pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_path)
        output_image_path = os.path.join(
            settings.MEDIA_ROOT, "converted", f"{os.path.splitext(pdf_file.name)[0]}.jpg")

        os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
        pdf_to_vertical_image(abs_pdf_path, output_image_path)

        image_url = os.path.join(
            settings.MEDIA_URL, "converted", f"{os.path.splitext(pdf_file.name)[0]}.jpg")

    return render(request, "pdf_to_image/upload.html", {"image_url": image_url})



