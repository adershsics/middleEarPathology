from django.db import models

# Create your models here.
# models.py

class Video(models.Model):
    file = models.FileField(upload_to='videos/')
