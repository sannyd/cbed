from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from cbed.authentication.views import (
    RegisterView,
    ResetPasswordView,
    SignInView,
    SignOutView,
    SSOView,
)

urlpatterns = [
    path(r"auth/signin", SignInView.as_view(), name="signin"),
    path(r"auth/register", RegisterView.as_view(), name="register"),
    path(r"auth/single_sign_on", SSOView.as_view(), name="single_sign_on"),
    path(r"auth/signout", SignOutView.as_view(), name="Sign Out View"),
    path(
        r"auth/request_reset_password",
        ResetPasswordView.as_view(),
        name="Reset Password View",
    ),
    path(r"auth/token-refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
