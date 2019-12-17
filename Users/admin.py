import csv
import datetime

from django.contrib import admin

# Register your models here.
from django.contrib.admin import SimpleListFilter
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.utils.html import strip_tags
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from Backend import settings
from Users.form import UserCreationForm, FacultyForm
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
        subject = 'SLIET Broadcast account verification success'
        queryset = queryset.filter(is_active=False)

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


class FacultyDepartmentFilter(SimpleListFilter):
    title = 'Department'
    parameter_name = 'department'

    def lookups(self, request, model_admin):
        departments = set([c for c in User.objects.filter(user_type="DEPARTMENT", is_admin=False)])
        return [(c.id, c.name) for c in departments]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(faculty_user__department=self.value())


class FacultyDetailAdmin(UserAdmin):
    list_filter = (FacultyDepartmentFilter, 'faculty_user__designation', 'is_admin', 'is_staff', 'is_active')
    list_display = (
        'username', 'name', 'designation', 'email', 'mobile', 'department', 'is_active', 'created_at', 'last_login')
    search_fields = ('email', 'username', 'name', 'mobile', 'faculty_user__designation')

    form = FacultyForm

    def get_queryset(self, request):
        return self.model.objects.filter(user_type="FACULTY", is_admin=False)

    @staticmethod
    def designation(faculty):
        return faculty.faculty_user.designation

    @staticmethod
    def department(faculty):
        try:
            return faculty.faculty_user.department.name
        except:
            return

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


class FacultyUser(User):
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
    list_filter = (DepartmentFilter, 'is_active', 'student_user__program', 'student_user__batch')
    search_fields = ('email', 'username', 'name', 'mobile', 'student_user__registration_number')
    list_display = (
        'username', 'name', 'email', 'mobile', 'batch', 'program', 'regd_no', 'is_active', 'created_at', 'last_login')

    actions = ['activate_user', 'export_as_csv']

    def get_queryset(self, request):
        return self.model.objects.filter(user_type="STUDENT", is_admin=False)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    @staticmethod
    def batch(student):
        return student.student_user.batch

    @staticmethod
    def program(student):
        return student.student_user.program

    def regd_no(self, student):
        return student.student_user.registration_number

    def export_as_csv(self, request, queryset):
        field_names = ['Name', 'Username', 'Email', 'Mobile', 'Department', 'Batch', 'Program', 'Regd. No.']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(
            'Student List ' + str(datetime.datetime.now()))
        writer = csv.writer(response)
        writer.writerow(field_names)
        data = queryset.values_list('name', 'username', 'email', 'mobile', 'student_user__department__name',
                                    'student_user__batch', 'student_user__program', 'student_user__registration_number')
        for obj in data:
            row = writer.writerow([value for value in obj])
        return response

    export_as_csv.short_description = "Export Selected list"

    regd_no.admin_order_field = 'student_user__registration_number'


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
admin.site.register(FacultyUser, FacultyDetailAdmin)
admin.site.register(Department, DepartmentAdmin)
