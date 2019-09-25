from django.contrib import admin

# Register your models here.
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError

from Users.models import User, Student, Faculty, Society
from Users.reverse_admin import ReverseModelAdmin, ReverseInlineModelAdmin


class StudentBaseAdmin(admin.StackedInline):
    model = Student
    fk_name = 'user'
    can_delete = False


class FacultyBaseAdmin(admin.StackedInline):
    model = Faculty
    fk_name = 'user'
    can_delete = False
    verbose_name = "Faculty Details"


class SocietyBaseAdmin(admin.StackedInline):
    model = Society
    fk_name = 'user'
    can_delete = False
    verbose_name = "Society Details"


class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'username', 'name', 'mobile')
    list_display = ('username', 'name', 'email', 'mobile', 'is_active', 'user_type', 'created_at', 'last_login')
    list_filter = ('user_type', 'is_admin', 'is_staff')
    ordering = ('-created_at',)
    fields = ('name', 'email', 'mobile', 'username', 'password', 'user_type', 'is_admin', 'is_staff', 'is_superuser')
    readonly_fields = ('is_superuser',)

    inlines = []

    def get_inline_instances(self, request, obj=None):
        inlines = self.inlines
        if obj and obj.user_type == "STUDENT":
            inlines = [StudentBaseAdmin, ]
        elif obj and obj.user_type == "FACULTY":
            inlines = [FacultyBaseAdmin, ]
        # elif obj and obj.user_type == "DEPARTMENT":
        #     inlines = [FacultyAdmin, ]
        elif obj and obj.user_type == "SOCIETY":
            inlines = [SocietyBaseAdmin, ]
        return [inline(self.model, self.admin_site) for inline in inlines]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if not request.user.is_superuser:
                return self.readonly_fields + ('username', 'is_staff',)  # have to check that staff user can add or not
            return self.readonly_fields + ('username',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.pk:
            try:
                orig_obj = User.objects.get(pk=obj.pk)
                if obj.password != orig_obj.password:
                    obj.set_password(obj.password)
            except:
                obj.set_password(obj.password)
        else:
            obj.set_password(obj.password)
        obj.save()


class StudentDetailAdmin(UserAdmin):
    inlines = [
        StudentBaseAdmin,
    ]

    def get_object(self, request, object_id, from_field=None):
        queryset = self.get_queryset(request)


class FacultyDetailAdmin(admin.ModelAdmin):
    list_display = ('name', 'department_name', 'designation', 'gender')
    fields = ('user', 'department', 'designation', 'sex', 'dob')

    #
    # fieldsets = (
    #     (None, {
    #         'fields': ('user', 'department',),
    #     }),
    # )

    @staticmethod
    def name(obj):
        if obj.user:
            return obj.user.name

    @staticmethod
    def department_name(obj):
        if obj.department:
            return obj.department.name

    @staticmethod
    def gender(obj):
        return obj.sex[0] + obj.sex[1:].lower()

    def get_queryset(self, request):
        query = super(FacultyDetailAdmin, self).get_queryset(request)
        filtered_query = query.filter(user__user_type='FACULTY')
        return filtered_query

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False
    #
    # def has_change_permission(self, request, obj=None):
    #     return False


class TestAdmin(ReverseModelAdmin):
    inline_type = "tabular",

    list_display = ('user', 'department', 'designation', 'sex', 'dob')
    inline_reverse = [
        ('user', {'fields': ('name', 'email', 'mobile', 'username', 'user_type',)}),
        ('department', {'fields': ['name', 'username']})
    ]


class Department(User):
    class Meta:
        proxy = True


class DepartmentAdmin(UserAdmin):
    def get_queryset(self, request):
        return self.model.objects.filter(user_type="DEPARTMENT")


admin.site.register(User, UserAdmin)
# admin.site.register(User, UserDetailAdmin)
admin.site.register(Student)
admin.site.register(Department, DepartmentAdmin)
