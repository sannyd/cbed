from django.db.models import TextChoices


class MemberPlanChoices(TextChoices):
    BABY_BAR_JUNE = "com.barexamdrills.app.babybarjune"
    BABY_BAR_OCT = "com.barexamdrills.app.babybaroct"
    PRO_BAR_FEB = "com.barexamdrills.app.probarfeb"
    PRO_BAR_JULY = "com.barexamdrills.app.probarjuly"
    TEST = "com.barexamdrills.app.unlockall"
    FREE = "free"
