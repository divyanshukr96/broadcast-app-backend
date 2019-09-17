from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from Users.models import User, Student


admin.site.register(User)
