import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

from Backend import settings
from Files.models import Files
from Notice.utils import compress_image
from Users.models import DEPARTMENT
from softdelete.models import SoftDeleteModel


class Notice(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notice_user')
    public_notice = models.BooleanField(default=True)
    department = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                        limit_choices_to={'user_type': DEPARTMENT, 'is_admin': False},
                                        related_name='notice_department')
    title = models.CharField(max_length=191, blank=False)
    description = models.TextField(blank=True)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    venue = models.CharField(max_length=100, null=True)
    is_event = models.BooleanField(default=False)
    visible = models.BooleanField(default=False)

    def __str__(self):
        return self.title[:15]


class Image(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(blank=True, upload_to='images/%Y/%m/%d/')
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.image = compress_image(self.image)
        super(Image, self).save(*args, **kwargs)


class NoticeHelperBase(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='User', on_delete=models.CASCADE)
    notice = models.ForeignKey(Notice, verbose_name='Notice', on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Bookmark(NoticeHelperBase):
    class Meta:
        db_table = "bookmarks"


class Interested(NoticeHelperBase):
    class Meta:
        db_table = "interested"


class NoticeView(NoticeHelperBase):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='User', on_delete=models.CASCADE, null=True)
    device_id = models.TextField(_('device id'))
    device_name = models.TextField(_('device name'), null=True)
    platform = models.CharField(_('device platform'), max_length=50)

    class Meta:
        db_table = "views"
