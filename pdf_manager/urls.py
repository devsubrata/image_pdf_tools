from django.urls import path
from . import views

app_name = 'pdf_manager'

urlpatterns = [
    path('extract/', views.extract_pages, name='extract'),
    path('combine/', views.combine_pdfs, name='combine'),
]
