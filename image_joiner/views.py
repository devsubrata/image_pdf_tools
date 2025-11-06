from django.shortcuts import render
from PIL import Image
import os
from django.conf import settings
from PyPDF2 import PdfReader, PdfWriter


def upload_images(request):
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        conversion_type = request.POST.get('image-pdf')

        if not images:
            return render(request, 'image_joiner/upload.html', {
                'error_message': 'No files selected. Please upload at least one image.'
            })

        if not conversion_type:
            return render(request, 'image_joiner/upload.html', {
                'error_message': 'Please select a conversion type.'
            })

        pil_images = []
        filenames = []
        for image_file in images:
            try:
                img = Image.open(image_file)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                pil_images.append(img)
                # Store filename (without extension)
                filenames.append(os.path.splitext(image_file.name)[0])
            except Exception:
                return render(request, 'image_joiner/upload.html', {
                    'error_message': 'One or more files are not valid images.'
                })

        if not pil_images:
            return render(request, 'image_joiner/upload.html', {
                'error_message': 'No valid images found.'
            })

        output_dir = os.path.join(settings.MEDIA_ROOT, 'joined')
        os.makedirs(output_dir, exist_ok=True)

        # Merge images vertically
        if conversion_type == 'images_to_image':
            max_width = max(img.width for img in pil_images)
            total_height = sum(img.height for img in pil_images)
            new_img = Image.new(
                'RGB', (max_width, total_height), (255, 255, 255))

            y_offset = 0
            for img in pil_images:
                new_img.paste(img, (0, y_offset))
                y_offset += img.height

            output_path = os.path.join(output_dir, 'joined_image.jpg')
            new_img.save(output_path)
            joined_image_url = settings.MEDIA_URL + 'joined/joined_image.jpg'

            return render(request, 'image_joiner/upload.html', {
                'joined_image_url': joined_image_url,
            })

        # 🆕 Improved PDF with bookmarks
        elif conversion_type == 'images_to_pdf':
            temp_pdf_path = os.path.join(output_dir, 'temp_joined.pdf')
            final_pdf_path = os.path.join(output_dir, 'joined_images.pdf')

            # Step 1: Save images as a basic multi-page PDF
            first_image, rest_images = pil_images[0], pil_images[1:]
            first_image.save(temp_pdf_path, save_all=True, append_images=rest_images)

            # Step 2: Add bookmarks using PyPDF2
            reader = PdfReader(temp_pdf_path)
            writer = PdfWriter()

            for i, page in enumerate(reader.pages):
                writer.add_page(page)
                # Add bookmark at page level using image name
                writer.add_outline_item(filenames[i], i)

            # Step 3: Write final PDF with bookmarks
            with open(final_pdf_path, "wb") as f:
                writer.write(f)

            # Clean up temporary file
            os.remove(temp_pdf_path)

            joined_pdf_url = settings.MEDIA_URL + 'joined/joined_images.pdf'

            return render(request, 'image_joiner/upload.html', {
                'joined_pdf_url': joined_pdf_url,
            })

        else:
            return render(request, 'image_joiner/upload.html', {
                'error_message': 'Invalid conversion type selected.'
            })

    # GET request
    return render(request, 'image_joiner/upload.html')
