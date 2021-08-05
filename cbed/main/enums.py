from django.db.models import IntegerChoices


class MemberPlanSimple(IntegerChoices):
    FREE = 0, "Free Bar"
    BABY = 100, "Baby Bar"
    PRO = 200, "Pro Bar"
