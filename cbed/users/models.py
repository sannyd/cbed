from django.contrib.auth.models import AbstractUser
from django.db.models import (
    SET_NULL,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    ImageField,
    Sum,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from cbed.main.consts import LevelNames
from cbed.main.enums import MemberPlanSimple
from cbed.transactions.enums import MemberPlanChoices


class User(AbstractUser):
    name = CharField(_("Name of User"), blank=True, max_length=255)
    avatar = ImageField(null=True, blank=True)
    state = CharField(max_length=64, default="")
    phone_number = PhoneNumberField(default="")
    member_plan = CharField(
        max_length=128,
        choices=MemberPlanChoices.choices,
        default=MemberPlanChoices.FREE,
    )
    membership = DateTimeField(default=timezone.now)
    current_mbe_section = ForeignKey(
        "main.Section",
        blank=True,
        null=True,
        on_delete=SET_NULL,
        limit_choices_to={"level__name": LevelNames.MBE_LEVEL_DRILLS},
        related_name="current_mbe_section",
    )
    current_fl_mcq_drill = ForeignKey(
        "main.Section",
        blank=True,
        null=True,
        on_delete=SET_NULL,
        limit_choices_to={"level__name": LevelNames.FL_MCQ_DRILLS},
        related_name="current_fl_mcq_drill",
    )
    is_unlock_essay_pt = BooleanField(default=False)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    @property
    def member_plan_simple(self):
        if self.member_plan in [
            MemberPlanChoices.BABY_BAR_OCT,
            MemberPlanChoices.BABY_BAR_JUNE,
        ]:
            return MemberPlanSimple.BABY
        elif self.member_plan in [
            MemberPlanChoices.PRO_BAR_JULY,
            MemberPlanChoices.PRO_BAR_FEB,
        ]:
            return MemberPlanSimple.PRO
        return MemberPlanSimple.FREE

    @property
    def points(self):
        return self.results.aggregate(Sum("correct"))["correct__sum"] or 0

    @property
    def last_section(self):
        return self.results.order_by("-created").first()

    @property
    def last_section_name(self):
        return self.current_mbe_section.name

    @points.setter
    def points(self, value):
        pass
