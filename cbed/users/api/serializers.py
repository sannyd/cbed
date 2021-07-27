import datetime
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from inapppy import AppStoreValidator, InAppPyValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from cbed.transactions.models import Transaction, MemberPlanChoices

User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "avatar",
            "name",
            "state",
            "member_plan",
            "member_plan_simple",
            "membership",
            "last_section_name",
            "points",
        ]


class UserUpdateInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["avatar", "name", "state"]


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
