from rest_framework.routers import DefaultRouter

from .api import BookmarkAPI, NoticeViewsViewSet, InterestedAPI, TempImageViewSet

router = DefaultRouter()

router.register(r'bookmark', BookmarkAPI)
router.register(r'interested', InterestedAPI)
router.register(r'views', NoticeViewsViewSet)
router.register(r'images', TempImageViewSet)


urlpatterns = router.urls
