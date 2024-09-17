from tempfile import NamedTemporaryFile
from urllib.request import urlopen

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
from django.core.files import File
from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework_simplejwt.tokens import RefreshToken

from cbed.authentication.sso_service import SSOService
from cbed.main.consts import LevelNames
from cbed.main.models import Level, Section
from cbed.users.models import User
from config.exception import (
    SSOMissingEmailAddressException,
    UserIsDeactivatedException,
    WrongAssociatedAccountException,
    WrongCredentialsException,
)


def fill_up_profile(user: User):
    mbe_level = Level.objects.filter(name=LevelNames.MBE_LEVEL_DRILLS).first()
    if mbe_level and user.current_mbe_section is None:
        start_mbe_section = (
            Section.objects.filter(
                level=mbe_level,
            )
            .order_by("order")
            .first()
        )
        user.current_mbe_section = start_mbe_section
        print(f"User {user} has been assigned to MBE_LEVEL_DRILLS.")

    mcq_level = Level.objects.filter(name=LevelNames.FL_MCQ_DRILLS).first()
    if mcq_level and user.current_fl_mcq_drill is None:
        start_mcq_section = (
            Section.objects.filter(
                level=mcq_level,
            )
            .order_by("order")
            .first()
        )
        user.current_fl_mcq_drill = start_mcq_section
        print(f"User {user} has been assigned to FL_MCQ_DRILLS.")

    ca_level = Level.objects.filter(name=LevelNames.CA_MCQ_DRILLS).first()
    if ca_level and user.current_ca_mcq_drill is None:
        start_ca_section = (
            Section.objects.filter(
                level=ca_level,
            )
            .order_by("order")
            .first()
        )
        user.current_ca_mcq_drill = start_ca_section
        print(f"User {user} has been assigned to CA_MCQ_DRILLS.")

    # MPRE_DRILLS
    mpre_level = Level.objects.filter(name=LevelNames.MPRE_DRILLS).first()
    if mpre_level and user.current_mpre_drill is None:
        start_mpre_section = (
            Section.objects.filter(
                level=mpre_level,
            )
            .order_by("order")
            .first()
        )
        user.current_mpre_drill = start_mpre_section
        print(f"User {user} has been assigned to MPRE_DRILLS.")

    # AGENCY_LEVEL
    agency_level = Level.objects.filter(name=LevelNames.AGENCY_LEVEL).first()
    if agency_level and user.current_agency_level is None:
        start_agency_section = (
            Section.objects.filter(
                level=agency_level,
            )
            .order_by("order")
            .first()
        )
        user.current_agency_level = start_agency_section
        print(f"User {user} has been assigned to AGENCY_LEVEL.")

    # PARTNERSHIPS_LEVEL
    partnerships_level = Level.objects.filter(
        name=LevelNames.PARTNERSHIPS_LEVEL
    ).first()
    if partnerships_level and user.current_partnerships_level is None:
        start_partnerships_section = (
            Section.objects.filter(
                level=partnerships_level,
            )
            .order_by("order")
            .first()
        )
        user.current_partnerships_level = start_partnerships_section
        print(f"User {user} has been assigned to PARTNERSHIPS_LEVEL.")

    # CORPS_LEVEL
    corps_level = Level.objects.filter(name=LevelNames.CORPS_LEVEL).first()
    if corps_level and user.current_corps_level is None:
        start_corps_section = (
            Section.objects.filter(
                level=corps_level,
            )
            .order_by("order")
            .first()
        )
        user.current_corps_level = start_corps_section
        print(f"User {user} has been assigned to CORPS_LEVEL.")

    # CONFLICTS_LEVEL
    conflicts_level = Level.objects.filter(name=LevelNames.CONFLICTS_LEVEL).first()
    if conflicts_level and user.current_conflicts_level is None:
        start_conflicts_section = (
            Section.objects.filter(
                level=conflicts_level,
            )
            .order_by("order")
            .first()
        )
        user.current_conflicts_level = start_conflicts_section
        print(f"User {user} has been assigned to CONFLICTS_LEVEL.")

    # FAM_LAW_LEVEL
    fam_law_level = Level.objects.filter(name=LevelNames.FAM_LAW_LEVEL).first()
    if fam_law_level and user.current_fam_law_level is None:
        start_fam_law_section = (
            Section.objects.filter(
                level=fam_law_level,
            )
            .order_by("order")
            .first()
        )
        user.current_fam_law_level = start_fam_law_section
        print(f"User {user} has been assigned to FAM_LAW_LEVEL.")

    # TRUSTS_LEVEL
    trusts_level = Level.objects.filter(name=LevelNames.TRUSTS_LEVEL).first()
    if trusts_level and user.current_trusts_level is None:
        start_trusts_section = (
            Section.objects.filter(
                level=trusts_level,
            )
            .order_by("order")
            .first()
        )
        user.current_trusts_level = start_trusts_section
        print(f"User {user} has been assigned to TRUSTS_LEVEL.")

    # WILLS_LEVEL
    wills_level = Level.objects.filter(name=LevelNames.WILLS_LEVEL).first()
    if wills_level and user.current_wills_level is None:
        start_wills_section = (
            Section.objects.filter(
                level=wills_level,
            )
            .order_by("order")
            .first()
        )
        user.current_wills_level = start_wills_section
        print(f"User {user} has been assigned to WILLS_LEVEL.")

    # SEC_TRANS_LEVEL
    sec_trans_level = Level.objects.filter(name=LevelNames.SEC_TRANS_LEVEL).first()
    if sec_trans_level and user.current_sec_trans_level is None:
        start_wills_section = (
            Section.objects.filter(
                level=sec_trans_level,
            )
            .order_by("order")
            .first()
        )
        user.current_sec_trans_level = start_wills_section
        print(f"User {user} has been assigned to SEC_TRANS_LEVEL.")

    user.save()


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
        fields = ["email", "password", "name", "state", "phone_number", "avatar"]

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

        user = User.objects.create(**validated_data)
        fill_up_profile(user)
        return user


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
            fill_up_profile(auth_user)
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
            user_email, avatar_url, name = SSOService.verify_google_auth(access_token)
        elif sso_type == "facebook":
            user_email, avatar_url, name = SSOService.verify_facebook_auth(access_token)
        else:
            raise SSOMissingEmailAddressException()
        auth_user: User
        auth_user, created = User.objects.get_or_create(
            username=user_email, email=user_email
        )

        if not auth_user.is_active:
            raise UserIsDeactivatedException()

        if avatar_url:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(avatar_url).read())
            img_temp.flush()
            auth_user.avatar.save(f"avatar_{auth_user.pk}", File(img_temp))
        if name:
            auth_user.name = name
            auth_user.save()
        fill_up_profile(auth_user)
        return auth_user


class ResetPasswordSerializer(AppSerializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        users = filter_users_by_email(email, is_active=True)

        if not users:
            raise ValidationError(
                "The e-mail address is not assigned to any user account"
            )
        if not users[0].password:
            raise ValidationError(
                "This email has already been associated with Google login. Please login with either of those methods."
            )

        return email

    def save(self):
        current_site = Site.objects.all().first()
        request = self.context["request"]
        email = self.validated_data["email"]

        for user in filter_users_by_email(email, is_active=True):
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
