# urls.py

from django.urls import path
from videotoimage_app import views

urlpatterns = [
    path('upload_video/', views.upload_video, name='upload_video'),
]