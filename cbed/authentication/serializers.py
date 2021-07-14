from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import EmailAwarePasswordResetTokenGenerator
from allauth.account.utils import (
    filter_users_by_email,
    user_pk_to_url_str,
    user_username,
)
from allauth.utils import build_absolute_uri
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.sites.models import Site
from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from cbed.authentication.sso_service import SSOService
from cbed.users.models import User
from config.exception import (
    WrongCredentialsException,
    WrongAssociatedAccountException,
    SSOMissingEmailAddressException,
    UserIsDeactivatedException,
)


class AppSerializer(Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RegisterSerializer(ModelSerializer):
    email = serializers.EmailField()
    name = serializers.CharField()
    state = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "name", "state", "avatar"]

    def validate_email(self, email):
        email = email.lower().strip()
        if email:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    {"email": "This email has been registered"}
                )
        return email

    def create(self, validated_data):
        password = validated_data["password"]
        validated_data["password"] = make_password(password)
        validated_data["username"] = validated_data["email"]

        return User.objects.create(**validated_data)


class SignInSerializer(AppSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return {"refresh": str(token), "access": str(token.access_token)}

    def create(self, validated_data):
        email = validated_data.get("email").lower()
        password = validated_data.get("password")
        try:
            auth_user = authenticate(username=email, password=password)
        except TypeError:
            raise WrongAssociatedAccountException()

        if auth_user and auth_user.is_active:
            return auth_user

        raise WrongCredentialsException()


class SSOSerializer(AppSerializer):
    access_token = serializers.CharField(write_only=True)
    sso_type = serializers.ChoiceField(choices=["google", "facebook"], write_only=True)
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return {"refresh": str(token), "access": str(token.access_token)}

    def create(self, validated_data):
        sso_type = validated_data.get("sso_type")
        access_token = validated_data.get("access_token")

        if sso_type == "google":
            user_email = SSOService.verify_google_auth(access_token)
        elif sso_type == "facebook":
            user_email = SSOService.verify_facebook_auth(access_token)
        else:
            raise SSOMissingEmailAddressException()

        auth_user, created = User.objects.get_or_create(
            username=user_email, email=user_email
        )

        if not auth_user.is_active:
            raise UserIsDeactivatedException()

        return auth_user


class ResetPasswordSerializer(AppSerializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        self.users = filter_users_by_email(email, is_active=True)
        if not self.users:
            raise ValidationError(
                "The e-mail address is not assigned" " to any user account"
            )
        return email

    def save(self):
        current_site = Site.objects.all().first()
        request = self.context["request"]
        email = self.validated_data["email"]
        for user in self.users:

            temp_key = EmailAwarePasswordResetTokenGenerator().make_token(user)
            path = reverse(
                "account_reset_password_from_key",
                kwargs=dict(uidb36=user_pk_to_url_str(user), key=temp_key),
            )
            url = build_absolute_uri(request, path)

            context = {
                "current_site": current_site,
                "user": user,
                "password_reset_url": url,
                "request": request,
            }

            if (
                app_settings.AUTHENTICATION_METHOD
                != app_settings.AuthenticationMethod.EMAIL
            ):
                context["username"] = user_username(user)
            get_adapter(request).send_mail(
                "account/email/password_reset_key", email, context
            )
        return self.validated_data["email"]
