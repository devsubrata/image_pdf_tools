from django.urls import path
from . import views

urlpatterns = [
    path('', views.songs_by_artist, name='songs_by_artist'),
    path('songs_by_artist', views.songs_by_artist, name='songs_by_artist'),
    path('top_youtube_songs', views.top_youtube_songs, name='top_youtube_songs'),
    path('api/youtube-search/', views.youtube_search, name='youtube_search'),
]
