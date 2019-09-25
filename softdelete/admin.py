from django.contrib import admin


# Register your models here.
class ParanoidAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'deleted_at', 'updated_at')
