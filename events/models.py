from django.db import models
# from djangotoolbox.fields import ListField
# Create your models here.
class Events(models.Model):
    """docstring for Events"""
    name = models.CharField(max_length=255)
    description = models.TextField()
