from django.contrib.auth import get_user_model
from rest_framework import serializers

from cbed.main.models import Level, Section, Question, Answer

User = get_user_model()


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class QuestionDetailSerializer(QuestionSerializer):
    answers = AnswerSerializer(many=True, read_only=True)


class SectionDetailSerializer(SectionSerializer):
    questions = QuestionDetailSerializer(many=True, read_only=True)


class SectionSearchSerializer(serializers.ModelSerializer):
    level_name = serializers.CharField(source='level.name')

    class Meta:
        model = Section
        fields = ["id", "name", "level_name"]


class LevelDetailSerializer(LevelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
