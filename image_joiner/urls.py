from django.urls import path
from .views import upload_images

urlpatterns = [
    path('', upload_images, name='upload_images'),
]
