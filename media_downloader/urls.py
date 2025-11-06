from django.urls import path
from .views import download_media

app_name = 'media_downloader'

urlpatterns = [
    path('', download_media, name='home'),
]
