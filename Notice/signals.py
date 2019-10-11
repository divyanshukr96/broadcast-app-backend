from django.db import transaction
from django.db.models import Q
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from fcm_django.models import FCMDevice

from Users.models import Student, Faculty
from .models import Notice

#
# def on_transaction_commit(func):
#     def inner(*args, **kwargs):
#         transaction.on_commit(lambda: func(*args, **kwargs))
#
#     return inner


def __following(user, notice, dept):
    if not isinstance(notice, Notice):
        return Q()
    following_query = Q(status=True, from_user__is_active=True)

    stud_or_fac = Q(from_user__student_user__department__in=dept) | Q(from_user__faculty_user__department__in=dept) | Q(
        from_user__in=dept) | Q(from_user__user_type__in=["SOCIETY", "CHANNEL"])

    if not notice.public_notice:
        following_query &= Q(from_user__user_type__in=["FACULTY", "DEPARTMENT"])  # ["FACULTY", "DEPARTMENT", "CHANNEL"]

    following = user.to_user.filter(following_query, stud_or_fac).exclude(from_user=user).values('from_user__name')

    return following


def __notification_from_department(user, notice, dept=None):
    student_query = Q(department=user, user__is_active=True, department__in=dept)
    if not notice.public_notice:
        student_query &= Q(user__user_type='FACULTY')
    following = __following(user, notice, dept=dept)
    student = Student.objects.filter(student_query).values("user__name")
    faculty = Faculty.objects.filter(student_query).values("user__name")
    return following.union(student, faculty)


def __notification_from_society(user, notice, dept=None):
    following = __following(user, notice, dept=dept)
    return following


def __send_notification(notice):
    if not isinstance(notice, Notice):
        return
    user = notice.user
    dept = notice.department.all()

    user_in = None
    if user.user_type == "DEPARTMENT" and not user.is_admin:
        user_in = __notification_from_department(user, notice, dept=dept)
    elif user.user_type in ["SOCIETY", "CHANNEL"]:
        user_in = __notification_from_society(user, notice, dept=dept)

    if not user.is_admin:
        device = FCMDevice.objects.all().filter(active=True, user__in=user_in)
    else:
        device = FCMDevice.objects.all().filter(active=True)
    return device


@receiver(m2m_changed, sender=Notice.department.through)
def post_save_handler(sender, **kwargs):
    notice = kwargs.get('instance', None)
    # created = kwargs.get('created', False)
    action = kwargs.get('action', None)
    # raw = kwargs.get('raw', False)

    if kwargs['pk_set']:
        # events = kwargs['model'].objects.filter(pk__in=kwargs['pk_set'])
        if action == 'post_add':
            if notice:
                __send_notification(notice)
        else:
            pass
