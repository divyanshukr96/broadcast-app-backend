import uuid

from django.db import models

# Create your models here.
from Backend import settings
# from Users.models import Department
from Users.models import DEPARTMENT


class Notice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notice_user')
    public_notice = models.BooleanField(default=True)
    department = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                        limit_choices_to={'user_type': DEPARTMENT}, related_name='notice_department')
    title = models.CharField(max_length=191, blank=False)
    description = models.TextField(blank=True)
    date = models.DateField(blank=True)
    time = models.TimeField(blank=True)
    venue = models.CharField(max_length=100, blank=True)

    # viewed = models.ManyToManyField(settings.AUTH_USER_MODEL, db_table='viewed', related_name='viewed', blank=True)

    def __str__(self):
        return self.title[:15]


