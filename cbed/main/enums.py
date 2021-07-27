from django.db.models import TextChoices


class MemberPlanSimple(TextChoices):
    FREE = "free", "Free Bar"
    BABY = "baby", "Baby Bar"
    PRO = "pro", "Pro Bar"
