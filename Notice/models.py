import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
from django.utils import timezone

from Backend import settings
# from Users.models import Department
from Users.models import DEPARTMENT
from softdelete.models import SoftDeleteModel


class Notice(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notice_user')
    public_notice = models.BooleanField(default=True)
    department = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                        limit_choices_to={'user_type': DEPARTMENT}, related_name='notice_department')
    title = models.CharField(max_length=191, blank=False)
    description = models.TextField(blank=True)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    venue = models.CharField(max_length=100, null=True)

    # viewed = models.ManyToManyField(settings.AUTH_USER_MODEL, db_table='viewed', related_name='viewed', blank=True)

    def __str__(self):
        return self.title[:15]


