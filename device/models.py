from __future__ import unicode_literals
from django.db import models
from django.utils import timezone

# Create your models here.

class Device(models.Model):
    ID = models.IntegerField(auto_created=True,primary_key=True)
    MODEL = models.TextField(max_length=15,null=False)
    IP = models.TextField(max_length=15,null=False)
    CPU = models.TextField(max_length=15,null=False)
    MEMORY = models.TextField(max_length=15,null=False)
    UPTIME = models.TextField(max_length=15,null=False)
    REBOOTED = models.TextField(max_length=15,null=False)
    CRASHED = models.TextField(max_length=15)
    INFORMATION = models.TextField(max_length=15)
    CREATED = models.DateTimeField(auto_created=True,default=timezone.now())

class Device_log(models.Model):
    ID = models.IntegerField(auto_created=True, primary_key=True)
    MODEL = models.TextField(max_length=15, null=False)
    IP = models.TextField(max_length=15, null=False)
    UPTIME = models.TextField(max_length=15, null=False)
    CRASHED = models.TextField(max_length=15)
    INFORMATION = models.TextField(max_length=15)
    CREATED = models.DateTimeField(auto_created=True,default=timezone.now())
