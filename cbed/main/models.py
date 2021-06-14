from django.contrib.auth import get_user_model
from django_better_admin_arrayfield.models.fields import ArrayField
from django.db import models

# Create your models here.
from model_utils.models import TimeStampedModel


class Level(TimeStampedModel):
    name = models.CharField(max_length=255)

    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ["order"]

    def __str__(self):
        return self.name


class Section(TimeStampedModel):
    name = models.CharField(max_length=255)
    youtube_urls = ArrayField(
        models.URLField(max_length=1000, blank=True), default=list, blank=True
    )
    pdf_urls = ArrayField(
        models.URLField(max_length=1000, blank=True), default=list, blank=True
    )
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="sections")

    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ["order"]

    def __str__(self):
        return self.name + " - " + self.level.name


class Question(TimeStampedModel):
    content = models.TextField()
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
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    correct = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
