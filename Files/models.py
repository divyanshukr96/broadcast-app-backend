from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from softdelete.models import SoftDeleteModel


class Files(SoftDeleteModel):
    name = models.CharField(max_length=50, blank=False)
    mime_type = models.CharField(max_length=20, blank=False)
    file = models.FileField(blank=True, upload_to='images/%Y/%m/%d/')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.name
