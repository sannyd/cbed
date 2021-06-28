from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.fields import BooleanField

from cbed.main.models import Level, Section, Question, Answer, Result

User = get_user_model()


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ["correct", "total"]


class LevelSerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = ["id", "name", "subtitle", "order", "is_available"]

    @swagger_serializer_method(BooleanField)
    def get_is_available(self, level: Level):
        current_user = self.context["request"].user
        available_sections_all = current_user.available_sections.all()
        for section in level.sections.all():
            if section.is_free or section in available_sections_all:
                return True
        return False


class SectionSerializer(serializers.ModelSerializer):
    last_result = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    @swagger_serializer_method(ResultSerializer)
    def get_last_result(self, section: Section):
        current_user = self.context["request"].user
        last_result = section.result_set.filter(user=current_user).first()
        return ResultSerializer(instance=last_result).data

    @swagger_serializer_method(BooleanField)
    def get_is_available(self, section: Section):
        current_user = self.context["request"].user
        return section.is_free or section in current_user.available_sections.all()

    class Meta:
        model = Section
        fields = [
            "id",
            "name",
            "subtitle",
            "image",
            "last_result",
            "is_available",
            "order",
        ]


class SectionSearchSerializer(SectionSerializer):
    level_name = serializers.CharField(source="level.name")

    class Meta:
        model = Section
        fields = [
            "id",
            "name",
            "subtitle",
            "image",
            "order",
            "level_name",
            "is_available",
        ]


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

    class Meta:
        model = Section
        fields = [
            "id",
            "name",
            "subtitle",
            "image",
            "last_result",
            "is_available",
            "youtube_urls",
            "pdf_urls",
            "questions",
        ]


class LevelDetailSerializer(LevelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Level
        fields = ["id", "name", "subtitle", "sections", "is_available"]
