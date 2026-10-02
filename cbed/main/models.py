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
    # GeoIP capture (added 2026-10-01) — populated by cbed.main.utils.capture_request_geo
    # on every save_result POST. Bypasses GA4's city-throttling.
    client_ip = models.GenericIPAddressField(blank=True, default=None, null=True)
    geo_city = models.CharField(blank=True, default='', max_length=255)
    geo_region = models.CharField(blank=True, default='', max_length=255)
    geo_country = models.CharField(blank=True, default='', max_length=2)
    geo_country_name = models.CharField(blank=True, default='', max_length=255)
    geo_source = models.CharField(
        blank=True, default='', max_length=32,
        help_text='cloudflare+ip-api, cloudflare_only, ip-api_only, or unavailable',
    )
    geo_captured_at = models.DateTimeField(blank=True, default=None, null=True)

    @property
    def grade(self):
        return int(100 * self.correct / self.total)


class Config(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True, default="")
    is_enable_login = models.BooleanField(default=True)
    is_enable_delete_account = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

class SubscriptionPlan(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name