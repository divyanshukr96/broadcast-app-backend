from django.contrib import admin

# Register your models here.
from django.contrib.admin import SimpleListFilter
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import get_template
from django.utils.html import strip_tags
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from Backend import settings
from Users.form import UserCreationForm
from Users.models import User, Student as StudentBase, Faculty, Society, Student
from Users.reverse_admin import ReverseModelAdmin, ReverseInlineModelAdmin


class StudentBaseAdmin(admin.StackedInline):
    model = StudentBase
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
    list_filter = ('user_type', 'is_admin', 'is_staff', 'is_active')
    ordering = ('-created_at',)
    fields = (
        'name', 'email', 'mobile', 'username', 'password', 'user_type', 'is_admin', 'is_staff', 'is_superuser',
        'profile', 'is_active')
    readonly_fields = ('is_superuser',)

    actions = ['activate_user']

    list_per_page = 15

    form = UserCreationForm

    inlines = []

    def activate_user(self, request, queryset):
        from django.core.mail import EmailMultiAlternatives
        subject = 'SLIET Broadcast account verification success'
        queryset = queryset.filter(is_active=False)
        # val = queryset.update(is_active=True)

        for user in queryset:
            user.is_active = True
            user.save()
            message = get_template('emails/account_activated.html').render({
                'user': user
            })
            user.email_user(subject, strip_tags(message), from_email=settings.EMAIL_HOST_USER, html_message=message)

    activate_user.short_description = "Activate selected user accounts"

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
            if obj == request.user:
                return self.readonly_fields + ('is_active',)
            if not request.user.is_superuser:
                return self.readonly_fields + ('username', 'is_staff',)  # have to check that staff user can add or not
            return self.readonly_fields + ('username', 'user_type')
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.pk:
            try:
                orig_obj = User.objects.get(pk=obj.pk)
                if obj.password != orig_obj.password:
                    token = Token.objects.get(user=orig_obj)
                    if token:
                        token.delete()
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
        return queryset


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


class SuperUser(User):
    class Meta:
        proxy = True


class Department(User):
    class Meta:
        proxy = True


class StudentUser(User):
    class Meta:
        proxy = True


class DepartmentFilter(SimpleListFilter):
    title = 'Department'
    parameter_name = 'department'

    def lookups(self, request, model_admin):
        departments = set([c for c in User.objects.filter(user_type="DEPARTMENT", is_admin=False)])
        return [(c.id, c.name) for c in departments]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(student_user__department=self.value())


class BatchFilter(SimpleListFilter):
    title = 'Batch'
    parameter_name = 'batch'

    def lookups(self, request, model_admin):
        departments = set([c for c in Student.objects.values_list('batch', flat=True).distinct()])
        return [(c, c) for c in departments]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(student_user__batch=self.value())


class StudentAdmin(UserAdmin):
    readonly_fields = ('is_superuser', 'is_admin', 'is_staff')
    list_filter = (DepartmentFilter, 'is_active', 'student_user__batch')

    def get_queryset(self, request):
        return self.model.objects.filter(user_type="STUDENT", is_admin=False)


class DepartmentAdmin(UserAdmin):
    def get_queryset(self, request):
        return self.model.objects.filter(user_type="DEPARTMENT", is_admin=False)

    def has_add_permission(self, request, obj=None):
        return False


class Administration(User):
    class Meta:
        proxy = True


class AdministratorAdmin(UserAdmin):
    def get_queryset(self, request):
        return self.model.objects.filter(user_type="DEPARTMENT", is_admin=True)

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(User, UserAdmin)
admin.site.register(Administration, AdministratorAdmin)
admin.site.register(SuperUser)
# admin.site.register(User, UserDetailAdmin)
admin.site.register(StudentUser, StudentAdmin)
admin.site.register(Department, DepartmentAdmin)
