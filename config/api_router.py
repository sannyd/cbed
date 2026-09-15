from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from cbed.main.views import (
    LevelViewSet,
    # iOS 11.0 scoreboard (legacy, shipped; uses is_tutor flag)
    ScoreBoardV110View,
    # iOS 11.1 scoreboard (new; uses is_tutor_for_bed flag)
    ScoreBoardV111View,
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
    # iOS 11.0 scoreboard (legacy) — backed by is_tutor
    path("scoreboard", ScoreBoardV110View.as_view()),
    # iOS 11.1 scoreboard (new in 11.1) — backed by is_tutor_for_bed
    path("scoreboard-111", ScoreBoardV111View.as_view()),
    path("config", GlobalConfigView.as_view()),
    path("all-config", AllGlobalConfigView.as_view()),
]
