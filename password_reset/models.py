import binascii
import datetime
import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from softdelete.models import SoftDeleteModel


class PasswordToken(SoftDeleteModel):
    """
    The default authorization token model.
    """
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='password_reset_token',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    otp = models.CharField(_("OTP"), max_length=8)

    class Meta:
        # Work around for a bug in Django:
        # https://code.djangoproject.com/ticket/19422
        #
        # Also see corresponding ticket:
        # https://github.com/encode/django-rest-framework/issues/705
        abstract = 'password_reset' not in settings.INSTALLED_APPS
        verbose_name = _("Password Token")
        verbose_name_plural = _("Password Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            self.otp = uuid.uuid4().hex.upper()[0:6]
        return super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

    def expired(self):
        timediff = datetime.datetime.now() - self.created_at
        return (timediff.seconds / 60) > 15
