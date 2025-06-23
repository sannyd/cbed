from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from cbed.main.views import (
    LevelViewSet,
    ScoreBoardView,
    SectionViewSet,
    GlobalConfigView, AllGlobalConfigView, SubscriptionPlanViewSet,
)
from cbed.users.api.views import PurchaseView, UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("profile", UserViewSet)
router.register("levels", LevelViewSet)
router.register("sections", SectionViewSet)
router.register("subscription-plans", SubscriptionPlanViewSet)

app_name = "api"
urlpatterns = router.urls + [
    path("purchase", PurchaseView.as_view()),
    path("scoreboard", ScoreBoardView.as_view()),
    path("config", GlobalConfigView.as_view()),
    path("all-config", AllGlobalConfigView.as_view()),
]
