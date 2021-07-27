from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel

from cbed.transactions.enums import MemberPlanChoices

User = get_user_model()


class Transaction(TimeStampedModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    product = models.CharField(max_length=128, choices=MemberPlanChoices.choices)
    ref = models.CharField(max_length=512, unique=True)
    info = models.TextField()
