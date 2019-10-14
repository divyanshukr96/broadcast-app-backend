from django.contrib import admin

# Register your models here.
from django.contrib.admin import SimpleListFilter

from Notice.models import Notice
from Users.models import User


class AdminFilter(SimpleListFilter):
    title = 'admin status'
    parameter_name = 'admin'

    def lookups(self, request, model_admin):
        return [(True, 'Yes'), (False, 'No')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__is_admin__exact=self.value())


class DepartmentFilter(SimpleListFilter):
    title = 'Department'
    parameter_name = 'department'

    def lookups(self, request, model_admin):
        departments = set([c for c in User.objects.filter(user_type="DEPARTMENT")])
        return [(c.id, c.name) for c in departments]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__id__exact=self.value())


class SocietyFilter(SimpleListFilter):
    title = 'Society Name'
    parameter_name = 'society'

    def lookups(self, request, model_admin):
        departments = set([c for c in User.objects.filter(user_type="SOCIETY")])
        return [(c.id, c.name) for c in departments]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__id__exact=self.value())


class AdministrationFilter(SimpleListFilter):
    title = 'Name'
    parameter_name = 'administration'

    def lookups(self, request, model_admin):
        departments = set([c for c in User.objects.filter(user_type="DEPARTMENT", is_admin=True)])
        return [(c.id, c.name) for c in departments]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__id__exact=self.value())


class PostByFilter(SimpleListFilter):
    title = 'Notice Publisher'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        countries = set([c.user for c in model_admin.model.objects.all()])
        return [(c.id, c.name) for c in countries]

    def queryset(self, request, queryset):
        if self.value() == 'AFRICA':
            return queryset.filter(user_type='DEPARTMENT')
        if self.value():
            return queryset.filter(user__id__exact=self.value())


class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'venue', 'user')
    list_filter = (DepartmentFilter, 'created_at', 'public_notice', AdminFilter, PostByFilter)
    search_fields = ('title', 'description', 'date', 'venue')
    fields = ('title', 'description', 'is_event', ('date', 'time'), 'venue', 'public_notice', 'department')
    list_per_page = 50


class SocietyNotice(Notice):
    class Meta:
        proxy = True


class SocietyNoticeAdmin(admin.ModelAdmin):
    list_filter = (SocietyFilter, 'created_at', 'public_notice', AdminFilter, PostByFilter)

    def get_queryset(self, request):
        return self.model.objects.filter(user__user_type="SOCIETY")


class AdministrationNotice(Notice):
    class Meta:
        proxy = True


class AdministrationNoticeAdmin(admin.ModelAdmin):
    list_filter = (AdministrationFilter, 'created_at', 'public_notice', AdminFilter, PostByFilter)

    def get_queryset(self, request):
        return self.model.objects.filter(user__user_type="DEPARTMENT", user__is_admin=True)


admin.site.register(Notice, NoticeAdmin)
admin.site.register(SocietyNotice, SocietyNoticeAdmin)
admin.site.register(AdministrationNotice, AdministrationNoticeAdmin)
