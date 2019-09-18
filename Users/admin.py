from django.contrib import admin

# Register your models here.
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError

from Users.models import User, Student, Faculty


class StudentAdmin(admin.StackedInline):
    model = Student
    fk_name = 'user'
    can_delete = False


class FacultyAdmin(admin.StackedInline):
    model = Faculty
    fk_name = 'user'
    can_delete = False
    verbose_name = "Faculty Details"


class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'username', 'name', 'mobile')
    list_display = ('username', 'name', 'email', 'mobile', 'is_active', 'user_type', 'date_joined', 'last_login')
    list_filter = ('user_type', 'is_admin', 'is_staff')
    ordering = ('-date_joined',)
    fields = ('name', 'email', 'mobile', 'username', 'password', 'user_type', 'is_admin', 'is_staff', 'is_superuser')
    readonly_fields = ('is_superuser',)

    inlines = []

    def get_inline_instances(self, request, obj=None):
        inlines = self.inlines
        if obj and obj.user_type == "STUDENT":
            inlines = [StudentAdmin, ]
        elif obj and obj.user_type == "FACULTY":
            inlines = [FacultyAdmin, ]
        # elif obj and obj.user_type == "DEPARTMENT":
        #     inlines = [FacultyAdmin, ]
        elif obj and obj.user_type == "SOCIETY":
            inlines = [FacultyAdmin, ]
        return [inline(self.model, self.admin_site) for inline in inlines]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if not request.user.is_superuser:
                return self.readonly_fields + ('username', 'is_staff',)  # have to check that staff user can add or not
            return self.readonly_fields + ('username',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.pk:
            orig_obj = User.objects.get(pk=obj.pk)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
        else:
            obj.set_password(obj.password)
        obj.save()


class StudentDetailAdmin(UserAdmin):
    inlines = [
        StudentAdmin,
    ]

    def get_object(self, request, object_id, from_field=None):
        queryset = self.get_queryset(request)


class FacultyDetailAdmin(UserAdmin):
    inlines = [
        FacultyAdmin,
    ]

    def get_queryset(self, request):
        query = super(FacultyDetailAdmin, self).get_queryset(request)
        filtered_query = query.filter(user_type='FACULTY')
        return filtered_query


admin.site.register(User, UserAdmin)
# admin.site.register(User, UserDetailAdmin)
