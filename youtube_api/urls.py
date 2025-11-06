from django.urls import path
from . import views

app_name = 'youtube_api'

urlpatterns = [
    path('', views.songs_by_artist, name='home'),
    path('songs_by_artist', views.songs_by_artist, name='artist_songs'),
    path('top_youtube_songs', views.top_youtube_songs, name='top_youtube_songs'),
    path('api/youtube-search/', views.youtube_search, name='youtube_search'),
]
