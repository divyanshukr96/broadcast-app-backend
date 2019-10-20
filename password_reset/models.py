import binascii
import datetime
import os
import uuid

from django.conf import settings
from django.db import models
from django.template.loader import get_template
from django.utils.html import strip_tags
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
        abstract = 'password_reset' not in settings.INSTALLED_APPS
        verbose_name = _("Password Token")
        verbose_name_plural = _("Password Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            self.otp = uuid.uuid4().hex.upper()[0:6]
            self.send_otp_mail()
        return super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

    def expired(self):
        time_diff = datetime.datetime.now() - self.created_at
        return (time_diff.seconds / 60) > 15

    def being_expired(self):
        time_diff = datetime.datetime.now() - self.created_at
        return (time_diff.seconds / 60) > 10

    def send_otp_mail(self):
        subject = 'Reset your SLIET Broadcast account password'
        message = get_template('emails/password_reset.html').render({
            'user': self.user,
            'otp': self.otp
        })
        self.user.email_user(subject, strip_tags(message), from_email=settings.EMAIL_HOST_USER, html_message=message)

    def send_success_mail(self):
        subject = 'Password change for SLIET Broadcast successful'
        message = get_template('emails/password_reset_success.html').render({
            'user': self.user,
        })
        self.user.email_user(subject, strip_tags(message), from_email=settings.EMAIL_HOST_USER, html_message=message)
