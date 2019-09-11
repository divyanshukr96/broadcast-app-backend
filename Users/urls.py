from rest_framework import routers
from .api import  FacultyViewSet, StudentViewSet, DepartmentViewSet
from Notice.api import NoticeViewSet


router = routers.DefaultRouter()
# router.register('user', UserViewSet, 'user')
router.register('faculty', FacultyViewSet, 'faculty')
router.register('student', StudentViewSet, 'student')
router.register('notice', NoticeViewSet, 'notice')
router.register('department', DepartmentViewSet, 'depart')

urlpatterns = router.urls
