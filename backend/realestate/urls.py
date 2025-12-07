from django.urls import path
from .views import analyze_query, download_data

urlpatterns = [
    path("analyze/", analyze_query, name="analyze-query"),
    path("download/", download_data, name="download-data"),
]
