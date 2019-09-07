from rest_framework import routers
from .api import UserViewSet
from Notice.api import NoticeViewSet, DepartmentViewSet


router = routers.DefaultRouter()
router.register('user', UserViewSet, 'user')
router.register('notice', NoticeViewSet, 'notice')
# router.register('department', DepartmentViewSet, 'depart')

urlpatterns = router.urls
