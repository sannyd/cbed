from django.db.models import TextChoices


class MemberPlan(TextChoices):
    FREE = "free", "Free Bar"
    BABY = "baby", "Baby Bar"
    PRO = "pro", "Pro Bar"
