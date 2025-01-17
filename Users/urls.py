from django.urls import path, re_path, include
from rest_framework import routers

from Users import views
from .api import RegisterAPI, PasswordUpdateAPI, ChannelAPI, ChannelFollowAPI, ChannelFollowingAPI, FacultyRegisterAPI, \
    UserDetailWithNotice
from .api import UserAPI, LoginAPI, PublicDepartmentAPI, UserUpdateAPI
from Notice.api import NoticeViewSet, PublicNoticeAPI, PrivateNoticeAPI, DeleteNoticeImage
from Notice.old.api import PublicNoticeAPI as OldPublicAPI, PrivateNoticeAPI as OldPrivateAPI

router = routers.DefaultRouter()
# router.register('user', UserViewSet, 'user')
# router.register('faculty', FacultyViewSet, 'faculty')
# router.register('student', StudentViewSet, 'student')
router.register('notice', NoticeViewSet, 'notice')
# router.register('department', DepartmentViewSet, 'depart')
# router.register('register', RegisterAPI, 'regot')

urlpatterns = [
    path('', include('Notice.urls')),
    path('', include('password_reset.urls')),
    path('appversion', views.app_version, name='program'),
    path('faculty', views.faculty, name='faculty'),
    path('auth/register', RegisterAPI.as_view()),
    path('auth/register/faculty', FacultyRegisterAPI.as_view()),
    path('auth/user', UserAPI.as_view()),
    path('auth/user/password', PasswordUpdateAPI.as_view()),
    path('auth/user/update', UserUpdateAPI.as_view()),
    path('auth/login', LoginAPI.as_view()),
    path('public/notice', OldPublicAPI.as_view()),
    path('private/notice', OldPrivateAPI.as_view()),
    path('v1/public/notice', PublicNoticeAPI.as_view()),
    path('v1/private/notice', PrivateNoticeAPI.as_view()),
    path('public/department', PublicDepartmentAPI.as_view()),
    path('public/program', views.program, name='program'),
    path('channel', ChannelAPI.as_view()),
    path('channel/following', ChannelFollowingAPI.as_view()),
    re_path('channel/follow/(?P<pk>[^/.]+)', ChannelFollowAPI.as_view({'post': 'create', 'delete': 'destroy'})),
    re_path('notice/(?P<pk_notice>[^/.]+)/image/(?P<pk>[^/.]+)', DeleteNoticeImage.as_view()),
    re_path('user/(?P<pk>[^/.]+)', UserDetailWithNotice.as_view({'get': 'retrieve'})),
]

urlpatterns += router.urls

# urlpatterns = router.urls
