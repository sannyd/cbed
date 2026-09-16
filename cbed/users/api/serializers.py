import datetime
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from inapppy import AppStoreValidator, InAppPyValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from cbed.transactions.models import MemberPlanChoices, Transaction

User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    current_mixed_mbe_section_id = serializers.IntegerField(read_only=True)
    # Per-section NextGen FK ids. Each names the user's current section in
    # that pipeline; the iOS scoreboard reads them when a non-MBE chip is
    # selected so each row's level label matches the chip's subject.
    # The wire names match `current_<section>` (no `_id` suffix), matching
    # the legacy ProfileInfoM contract in the iOS app.
    current_drafting_section = serializers.IntegerField(
        source="current_drafting_section_id", read_only=True)
    current_counseling_section = serializers.IntegerField(
        source="current_counseling_section_id", read_only=True)
    current_ng_spt_section = serializers.IntegerField(
        source="current_ng_spt_section_id", read_only=True)
    current_ng_lrpt_section = serializers.IntegerField(
        source="current_ng_lrpt_section_id", read_only=True)
    # NG MCQ sections already come through these names on ProfileInfoM
    # natively (the FK columns are listed in fields).
    # Email & Zoom package flag (alias for `is_tutor`). The iOS Settings
    # screen reads this to decide whether to expose essay/mpt counters.
    is_email_zoom = serializers.BooleanField(source="is_tutor", read_only=True)

    # Resolved section names. Mirrors the per-section FK columns above:
    # each SerializerMethodField reads the FK and pulls Section.name.
    current_drafting_section_name = serializers.SerializerMethodField()
    current_counseling_section_name = serializers.SerializerMethodField()
    current_ng_spt_section_name = serializers.SerializerMethodField()
    current_ng_lrpt_section_name = serializers.SerializerMethodField()
    current_ng_mcq_1_choice_section_name = serializers.SerializerMethodField()
    current_ng_mcq_2_choice_section_name = serializers.SerializerMethodField()

    def _section_name(self, user, attr):
        section = getattr(user, attr, None)
        if section is None:
            return None
        return getattr(section, "name", None) or str(section)

    def get_current_drafting_section_name(self, user):
        return self._section_name(user, "current_drafting_section")

    def get_current_counseling_section_name(self, user):
        return self._section_name(user, "current_counseling_section")

    def get_current_ng_spt_section_name(self, user):
        return self._section_name(user, "current_ng_spt_section")

    def get_current_ng_lrpt_section_name(self, user):
        return self._section_name(user, "current_ng_lrpt_section")

    def get_current_ng_mcq_1_choice_section_name(self, user):
        return self._section_name(user, "current_ng_mcq_1_choice_section")

    def get_current_ng_mcq_2_choice_section_name(self, user):
        return self._section_name(user, "current_ng_mcq_2_choice_section")

    class Meta:
        model = User
        fields = [
            "email",
            "avatar",
            "name",
            "state",
            "phone_number",
            "member_plan",
            "member_plan_simple",
            "membership",
            "last_section_name",
            "points",
            "is_tutor",
            "essay_count",
            "mpt_count",
            "current_mixed_mbe_section_id",
            "current_drafting_section",
            "current_counseling_section",
            "current_ng_spt_section",
            "current_ng_lrpt_section",
            "current_ng_mcq_1_choice_section_id",
            "current_ng_mcq_2_choice_section_id",
            "current_drafting_section_name", "current_counseling_section_name",
            "current_ng_spt_section_name", "current_ng_lrpt_section_name",
            "current_ng_mcq_1_choice_section_name", "current_ng_mcq_2_choice_section_name",
            "is_email_zoom",
        ]


class UserUpdateInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "avatar",
            "name",
            "state",
            "phone_number",
            "essay_count",
            "mpt_count",
        ]


class ReceiptSerializer(serializers.Serializer):
    receipt_data = serializers.CharField()

    def update(self, instance, validated_data):
        pass

    def validate_receipt_data(self, value):
        try:
            validator = AppStoreValidator(
                settings.BUNDLE_ID,
                auto_retry_wrong_env_request=settings.AUTO_RETRY_WRONG_ENV_REQUEST,
            )

            result = validator.validate(value, None, exclude_old_transactions=True)

            if in_app := result["receipt"]["in_app"]:
                in_app = sorted(in_app, key=lambda k: k["purchase_date_ms"])
                last_purchase = in_app[-1]
                product_id = last_purchase["product_id"]
                transaction_id = last_purchase["transaction_id"]
                if Transaction.objects.filter(ref=transaction_id).first():
                    raise ValidationError("Purchase existed!")

                user = self.context["request"].user
                user.member_plan = product_id
                now = timezone.now()
                if product_id == MemberPlanChoices.BABY_BAR_JUNE:
                    membership = now.replace(day=30, month=6)
                elif product_id == MemberPlanChoices.TEST:
                    membership = now.replace(day=30, month=10)
                elif product_id == MemberPlanChoices.BABY_BAR_OCT:
                    membership = now.replace(day=30, month=10)
                elif product_id == MemberPlanChoices.PRO_BAR_FEB:
                    membership = now.replace(day=28, month=2)
                elif product_id == MemberPlanChoices.PRO_BAR_JULY:
                    membership = now.replace(day=30, month=7)
                else:
                    raise ValidationError("Not supported product")

                Transaction.objects.create(
                    user=user,
                    product=product_id,
                    ref=transaction_id,
                    info=json.dumps(result, indent=4),
                )

                if membership < now:
                    membership += datetime.timedelta(days=366)

                user.membership = membership
                user.save()

                return f"Buy successful {user.get_member_plan_display()} to {user.membership.date()}"
            raise ValidationError("No purchase found")
        except InAppPyValidationError as e:
            raise ValidationError(e)

    def create(self, validated_data):
        return validated_data
