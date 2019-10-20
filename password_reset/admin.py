from django.contrib import admin

from .models import PasswordToken


class PasswordTokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created_at')
    fields = ('user',)
    ordering = ('-created_at',)


admin.site.register(PasswordToken, PasswordTokenAdmin)
