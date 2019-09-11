from django.db import models

# Create your models here.


class Files(models.Model):
    name = models.CharField(max_length=50,blank=False)
    mime_type = models.CharField(max_length=20,blank=False)
    file = models.FileField(blank=True,upload_to='images/%Y/%m/%d/')

