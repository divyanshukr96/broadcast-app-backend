from django.core import validators
from django.utils.deconstruct import deconstructible

from django.utils.translation import gettext_lazy as _


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r'^[\w_]+$'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and underscore characters.'
    )
    flags = 0


@deconstructible
class MobileValidator(validators.RegexValidator):
    regex = r'^\s*(?:\+?(\d{1,3}))?[- (]*(\d{3})[- )]*(\d{3})[- ]*(\d{4})(?: *[x/#]{1}(\d+))?\s*$'
    message = _(
        'Enter a valid mobile number.'
    )
    flags = 0


@deconstructible
class RegistrationNoValidator(validators.RegexValidator):
    regex = r''
    message = _(
        'Enter a valid mobile number.'
    )
    flags = 0
