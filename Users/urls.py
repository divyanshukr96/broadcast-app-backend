from django.urls import path, re_path
from rest_framework import routers

from Users import views
from .api import FacultyViewSet, StudentViewSet, DepartmentViewSet, RegisterAPI, PasswordUpdateAPI, ChannelAPI, \
    ChannelFollowAPI, ChannelFollowingAPI
from .api import UserAPI, LoginAPI, PublicDepartmentAPI, UserUpdateAPI
from Notice.api import NoticeViewSet, PublicNoticeAPI, PrivateNoticeAPI, DeleteNoticeImage

router = routers.DefaultRouter()
# router.register('user', UserViewSet, 'user')
# router.register('faculty', FacultyViewSet, 'faculty')
# router.register('student', StudentViewSet, 'student')
router.register('notice', NoticeViewSet, 'notice')
# router.register('department', DepartmentViewSet, 'depart')
# router.register('register', RegisterAPI, 'regot')

urlpatterns = [
    path('auth/register', RegisterAPI.as_view()),
    path('auth/user', UserAPI.as_view()),
    path('auth/user/password', PasswordUpdateAPI.as_view()),
    path('auth/user/update', UserUpdateAPI.as_view()),
    path('auth/login', LoginAPI.as_view()),
    path('public/notice', PublicNoticeAPI.as_view()),
    path('public/department', PublicDepartmentAPI.as_view()),
    path('public/program', views.program, name='program'),
    path('private/notice', PrivateNoticeAPI.as_view()),
    path('channel', ChannelAPI.as_view()),
    path('channel/following', ChannelFollowingAPI.as_view()),
    re_path('channel/follow/(?P<pk>[^/.]+)', ChannelFollowAPI.as_view({'post': 'create', 'delete': 'destroy'})),
    re_path('notice/(?P<pk_notice>[^/.]+)/image/(?P<pk>[^/.]+)', DeleteNoticeImage.as_view()),
]

urlpatterns += router.urls

# urlpatterns = router.urls
