from django.urls import path
from . import views

app_name = 'subtitle_extractor'

urlpatterns = [
    path('', views.subtitle_extractor_view, name='subtitle_extractor'),
]
