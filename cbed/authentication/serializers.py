from uuid import uuid4

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.serializers import Serializer
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


class RegisterSerializer(AppSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        email = validated_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "This email has been registered"}
            )
        password = validated_data["password"]

        return User.objects.create(
            username=email,
            email=email,
            password=make_password(password),
        )


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

        auth_user = User.objects.filter(email=user_email).first()

        if not auth_user:
            auth_user = User.objects.create(
                username=user_email,
                email=user_email,
            )

        if auth_user and not auth_user.is_active:
            raise UserIsDeactivatedException()

        return auth_user
