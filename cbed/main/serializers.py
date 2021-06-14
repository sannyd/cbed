from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from cbed.main.models import Level, Section, Question, Answer, Result

User = get_user_model()


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ["correct", "total"]


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    last_result = serializers.SerializerMethodField()

    @swagger_serializer_method(ResultSerializer)
    def get_last_result(self, section: Section):
        current_user = self.context["request"].user
        last_result = section.result_set.filter(user=current_user).first()
        return ResultSerializer(instance=last_result).data

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
