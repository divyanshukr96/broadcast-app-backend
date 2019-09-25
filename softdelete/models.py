from django.db import models
from django.utils.timezone import now


class SoftDeleteModelManager(models.Manager):
    def get_queryset(self):
        return super(SoftDeleteModelManager, self).get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    objects = SoftDeleteModelManager()
    objects_with_deleted = models.Manager()

    class Meta:
        abstract = True

    def delete(self, hard=False, **kwargs):
        if hard:
            super(SoftDeleteModel, self).delete()
        else:
            self.deleted_at = now()
            self.save()
