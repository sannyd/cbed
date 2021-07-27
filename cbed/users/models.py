from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, DateTimeField, ManyToManyField, ImageField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from cbed.main.enums import MemberPlanSimple
from cbed.transactions.enums import MemberPlanChoices


class User(AbstractUser):
    name = CharField(_("Name of User"), blank=True, max_length=255)
    avatar = ImageField(null=True, blank=True)
    state = CharField(max_length=64, default="")
    member_plan = CharField(max_length=128, choices=MemberPlanChoices.choices, default=MemberPlanChoices.FREE)
    membership = DateTimeField(default=timezone.now)
    available_sections = ManyToManyField("main.Section")
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    @property
    def member_plan_simple(self):
        if self.member_plan in [MemberPlanChoices.BABY_BAR_OCT, MemberPlanChoices.BABY_BAR_JUNE]:
            return MemberPlanSimple.BABY
        elif self.member_plan in [MemberPlanChoices.PRO_BAR_JULY, MemberPlanChoices.PRO_BAR_FEB]:
            return MemberPlanSimple.PRO
        return MemberPlanSimple.FREE
