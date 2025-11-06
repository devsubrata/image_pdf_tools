from django.urls import path
from .views import upload_images

app_name = 'image_joiner'

urlpatterns = [
    path('', upload_images, name='home'),  # renamed from 'join' → 'home'
]
