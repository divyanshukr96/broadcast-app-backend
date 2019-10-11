from django.test import TestCase

# Create your tests here.


# device = self.request.user.fcmdevice_set.filter(active=True)

# device.send_message("Title", "Message")
# device.send_message(data={"test": "test"})
# device.send_message(title="Title", body="Message", data={"test": "test"})

# from_user__student_user__department = self.request.user

# ffh = self.request.user.to_user.filter(status=True, from_user__is_active=True).exclude(
#     from_user=self.request.user).values('from_user__name')
#
# ss = Student.objects.filter(department=self.request.user).values('user__name')
# ff = Faculty.objects.filter(department=self.request.user, user__in=ffh).values('user__name')
# print(ss)
# print(ff)
# print(ss.union(ff, ffh))
# print(dir(ff))
# print(ff.values('from_user'))
# device = FCMDevice.objects.all().filter(user__in=ff.values('from_user'))
# device = FCMDevice.objects.all().filter(user__in=ff)
# device = FCMDevice.objects.all().filter(user__in=ss.union(ff, ffh))
# print(device.send_message("Computer Science Engineering", "Tomorrow is no lecture"))
# print(ff.first().from_user)
# print(dir(ff.first().from_user))


# device = FCMDevice.objects.filter(active=True).latest('date_created')
#
# icon = "data:image/png;base64,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"
# device.send_message("Computer Science Engineering", "Tomorrow is no lecture", sound='Default',
#                     # extra_kwargs={
#                     #     "image": "http://simpleicon.com/wp-content/uploads/cute.png",
#                     # },
#                     click_action='FLUTTER_NOTIFICATION_CLICK')
