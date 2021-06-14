from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from cbed.main.views import LevelViewSet, SectionViewSet
from cbed.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("levels", LevelViewSet)
router.register("sections", SectionViewSet)

app_name = "api"
urlpatterns = router.urls
