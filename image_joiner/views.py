from django.shortcuts import render
from PIL import Image
import os
from django.conf import settings


def upload_images(request):
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        # 'on' for whichever radio is selected
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
        for image_file in images:
            try:
                img = Image.open(image_file)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                pil_images.append(img)
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
        # Save images as multi-page PDF
        elif conversion_type == 'images_to_pdf':  
            output_path = os.path.join(output_dir, 'joined_images.pdf')
            first_image, rest_images = pil_images[0], pil_images[1:]
            first_image.save(output_path, save_all=True, append_images=rest_images)

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


# print("POST Data:", request.POST)
# print("FILES Data:", request.FILES)
# print("Conversion type:", request.POST.get('image-pdf'))
# print("Uploaded images:", request.FILES.getlist('images'))
# print("User Agent:", request.headers.get('User-Agent'))
# print("All headers:", dict(request.headers))
# print("GET Params:", request.GET)  # similar to req.query in Node.js
# print("Raw Body:", request.body.decode('utf-8'))

# def upload_images(request):
#     print("Method:", request.method)
#     print("POST data:", request.POST)
#     print("FILES:", request.FILES)
#     print("Headers:", request.headers)
#     print("GET params:", request.GET)
#     return HttpResponse("Check console")
