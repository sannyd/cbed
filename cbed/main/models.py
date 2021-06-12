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
    youtube_url = models.CharField(max_length=1000, blank=True)
    pdf_url = models.CharField(max_length=1000, blank=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ["order"]

    def __str__(self):
        return self.name + " - " + self.level.name


class Question(TimeStampedModel):
    content = models.TextField()
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ["order"]


class Answer(TimeStampedModel):
    content = models.TextField()
    discussion = models.TextField()
    is_correct = models.BooleanField()

    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ["order"]
