from rest_framework.routers import DefaultRouter

from .api import BookmarkAPI, NoticeViewsViewSet

router = DefaultRouter()

router.register(r'bookmark', BookmarkAPI)
router.register(r'views', NoticeViewsViewSet)


urlpatterns = router.urls
