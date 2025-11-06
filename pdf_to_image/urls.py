from django.urls import path
from .views import upload_pdf

app_name = 'pdf_to_image'

urlpatterns = [
    path('', upload_pdf, name='home'),
]
