import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.utils.timezone import now
from rest_framework.utils import json

from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _

from Files.models import Files
from Notice.utils import compress_image
from Users.manager import UserManager
from Users.validators import UsernameValidator, MobileValidator
from softdelete.models import SoftDeleteModel

GENDER_CHOICE = [('MALE', 'MALE'), ('FEMALE', 'FEMALE'), ('OTHER', 'OTHER')]

DEPARTMENT = 'DEPARTMENT'
SOCIETY = 'SOCIETY'
FACULTY = 'FACULTY'
STUDENT = 'STUDENT'
CHANNEL = 'CHANNEL'
# ADMIN = 'ADMIN'

USER_TYPES = [
    (DEPARTMENT, 'Department'),
    (SOCIETY, 'Society'),
    (FACULTY, 'Faculty'),
    (STUDENT, 'Student'),
    (CHANNEL, 'Channel'),
    # (ADMIN, 'Admin'),
]


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UsernameValidator()
    mobile_validator = MobileValidator()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        null=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and underscore only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    name = models.CharField(_('full name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), unique=True, blank=True)
    mobile = models.CharField(
        _('mobile'), max_length=15, unique=True, blank=True, null=True, validators=[mobile_validator],
        error_messages={
            'unique': _("A user with that mobile already exists."),
        },
    )

    about = models.TextField(_('about'), blank=True)
    profile = models.ImageField(_('profile image'), blank=True, upload_to='profile/%Y/%m/', null=True)
    _extra_fields = models.TextField(_('extra fields'), blank=True, db_column="extra_fields")

    user_type = models.CharField(_('user type'), max_length=15, choices=USER_TYPES, default='STUDENT')

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_admin = models.BooleanField(
        _('admin status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    objects_with_deleted = models.Manager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def __str__(self):
        username = self.get_username()
        if not username and self.user_type == FACULTY:
            return ''
        return username

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """Return the full name for the user."""
        return self.name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        if self.name:
            return self.name.split()[0].strip()
        return self.name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def delete(self, hard=False, **kwargs):
        if hard:
            super(AbstractUser, self).delete()
        else:
            self.deleted_at = now()
            self.save()

    @property
    def extra_fields(self):
        try:
            if self._extra_fields:
                return eval(self._extra_fields)
        except:
            pass
        return {}

    @extra_fields.setter
    def extra_fields(self, value):
        self._extra_fields = value

    def save(self, *args, **kwargs):
        if self.profile:
            self.profile = compress_image(self.profile)
        super(AbstractUser, self).save(*args, **kwargs)

    #
    # def save(self, *args, **kwargs):
    #     print(self.clean_fields('profile'))
    #     super().save(*args, **kwargs)
    #     # if self._password is not None:
    #     #     password_validation.password_changed(self._password, self)
    #     #     self._password = None


class User(AbstractUser):
    """
    Users within the Django authentication system are represented by this
    model.

    Username and password are required. Other fields are optional.
    """

    followers = models.ManyToManyField('self', through='Follower', symmetrical=False, related_name='following_to')

    # interested = models.ManyToManyField(Notice, db_table='interested', related_name='interested')

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_following(self):
        return self.followers.filter(
            to_user__status=True,
            to_user__from_user=self)

    def add_follower(self, to, status):
        if not status:
            return self.__remove_follower(to=to)
        follow, created = Follower.objects.get_or_create(
            from_user=self,
            to_user=to,
        )
        if not created:
            follow.status = True
            follow.save()
        return follow

    def __remove_follower(self, to):
        Follower.objects.filter(
            from_user=self,
            to_user=to,
            status=True
        ).update(status=False)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_user',
                                limit_choices_to={'user_type': STUDENT}, primary_key=True)
    department = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_department',
                                   limit_choices_to={'user_type': DEPARTMENT, 'is_admin': False})
    registration_number = models.CharField(max_length=8, blank=False)
    batch = models.IntegerField(blank=False, null=True)
    program = models.CharField(max_length=80, blank=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICE, blank=False)
    dob = models.DateField(_('Date of Birth'), blank=True, null=True)

    def __str__(self):
        return self.user.name


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_user',
                                limit_choices_to={'user_type': FACULTY}, primary_key=True)

    department = models.ForeignKey(User, on_delete=models.CASCADE, related_name='faculty_department',
                                   limit_choices_to={'user_type': DEPARTMENT, 'is_admin': False})

    designation = models.CharField(max_length=80, blank=False)

    gender = models.CharField(_('Gender'), max_length=10, choices=GENDER_CHOICE, blank=False)

    dob = models.DateField(_('Date of Birth'), blank=True, null=True)

    def __str__(self):
        return self.user.name


class Society(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='society_user',
                                limit_choices_to={'user_type': SOCIETY}, primary_key=True)
    registration_number = models.CharField(max_length=20, null=True)
    faculty_adviser = models.CharField(max_length=20, null=True)
    convener = models.CharField(max_length=20, null=True)


class Follower(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    status = models.BooleanField(default=True)

    @staticmethod
    def is_following(channel, user):
        try:
            if channel.is_admin:
                return True
            if Follower.objects.filter(to_user=channel, from_user=user, status=True):
                return True
        except:
            pass
        return False
