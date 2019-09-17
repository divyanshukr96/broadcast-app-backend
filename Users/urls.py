from django.urls import path
from rest_framework import routers
from .api import FacultyViewSet, StudentViewSet, DepartmentViewSet, RegisterAPI, UserAPI, LoginAPI
from Notice.api import NoticeViewSet


router = routers.DefaultRouter()
# router.register('user', UserViewSet, 'user')
router.register('faculty', FacultyViewSet, 'faculty')
router.register('student', StudentViewSet, 'student')
router.register('notice', NoticeViewSet, 'notice')
router.register('department', DepartmentViewSet, 'depart')
# router.register('register', RegisterAPI, 'regot')

urlpatterns = [
    path('auth/register', RegisterAPI.as_view()),
    path('auth/user', UserAPI.as_view()),
    path('auth/login', LoginAPI.as_view())
]


urlpatterns += router.urls

# urlpatterns = router.urls
