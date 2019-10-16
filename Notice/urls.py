from rest_framework.routers import DefaultRouter

from .api import BookmarkAPI, NoticeViewsViewSet, InterestedAPI

router = DefaultRouter()

router.register(r'bookmark', BookmarkAPI)
router.register(r'interested', InterestedAPI)
router.register(r'views', NoticeViewsViewSet)


urlpatterns = router.urls
