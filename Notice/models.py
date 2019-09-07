import uuid

from django.db import models

# Create your models here.
from Backend import settings


class Notice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    public_notice = models.BooleanField(default=True)
    department = models.ManyToManyField('Department', blank=True)
    title = models.CharField(max_length=191,blank=False)
    description = models.TextField(blank=True)
    date = models.DateField(blank=True)
    time = models.TimeField(blank=True)
    venue = models.CharField(max_length=100,blank=True)

    viewed = models.ManyToManyField(settings.AUTH_USER_MODEL, db_table='viewed', related_name='viewed', blank=True)

    def __str__(self):
        return self.title[:15]


class Department(models.Model):
    name = models.TextField(max_length=200)
    short_name = models.TextField(max_length=10)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name
