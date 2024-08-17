from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField
from model_utils.models import TimeStampedModel

from cbed.main.enums import MemberPlanSimple


class Level(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    subtitle = models.TextField(default="", blank=True)
    member_plan = models.IntegerField(
        choices=MemberPlanSimple.choices, default=MemberPlanSimple.FREE
    )

    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    is_drills_and_videos = models.BooleanField(default=False)

    class Meta(object):
        ordering = ["order"]

    def __str__(self):
        return self.name


class Section(TimeStampedModel):
    name = models.CharField(max_length=255)
    subtitle = models.TextField(default="", blank=True)
    member_plan = models.IntegerField(
        choices=MemberPlanSimple.choices, default=MemberPlanSimple.FREE
    )
    image = models.ImageField(default="", blank=True)
    youtube_urls = ArrayField(
        models.CharField(max_length=1000, blank=True), default=list, blank=True
    )
    pdf_urls = ArrayField(
        models.CharField(max_length=1000, blank=True), default=list, blank=True
    )
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="sections")
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ["order"]

    def __str__(self):
        return self.name + " - " + self.level.name


class Question(TimeStampedModel):
    content = models.TextField()
    youtube_url = models.CharField(max_length=1000, blank=True)
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="questions"
    )

    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ["order"]


class Answer(TimeStampedModel):
    content = models.TextField()
    discussion = models.TextField()
    is_correct = models.BooleanField()

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )

    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ["order"]


class Result(TimeStampedModel):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="results"
    )
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    correct = models.IntegerField(default=0)
    total = models.IntegerField(default=1, validators=[MinValueValidator(1)])

    @property
    def grade(self):
        return int(100 * self.correct / self.total)


class Config(models.Model):
    is_enable_login = models.BooleanField(default=True)
    is_enable_delete_account = models.BooleanField(default=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        if Config.objects.count() > 1:
            raise Exception("Only one Config object is allowed")
