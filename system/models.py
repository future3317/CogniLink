from django.db import models

# Create your models here.

class Account(models.Model):
    email=models.CharField(max_length=200, default='abc')
    password=models.CharField(max_length=200)
    name=models.CharField(max_length=20)

