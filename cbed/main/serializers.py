from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.fields import BooleanField

from cbed.main.consts import LevelNames
from cbed.main.models import Answer, Level, Question, Result, Section
from cbed.users.models import User


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ["correct", "total"]


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ["id", "name", "subtitle", "order"]


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
        if section.name == "Torts - Level 1" or section.name == "Level 1 - FL MCQ" or "Free" in section.level.name:
            return True

        current_user: User = self.context["request"].user
        if section.level.name == LevelNames.MBE_LEVEL_DRILLS:
            if (
                current_user.current_mbe_section
                and section.order <= current_user.current_mbe_section.order
            ):
                return True
            return False
        if section.level.name == LevelNames.FL_MCQ_DRILLS:
            if (
                current_user.current_fl_mcq_drill
                and section.order <= current_user.current_fl_mcq_drill.order
            ):
                return True
            return False
        if section.level.name == LevelNames.CA_MCQ_DRILLS:
            if (
                current_user.current_ca_mcq_drill
                and section.order <= current_user.current_ca_mcq_drill.order
            ):
                return True
            return False
        if section.level.name == LevelNames.MPRE_DRILLS:
            if (
                current_user.current_mpre_drill
                and section.order <= current_user.current_mpre_drill.order
            ):
                return True
            return False
        return True

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


class HighScoreUserDetail(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "avatar", "points", "last_section_name"]


class HighScoreResultSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    baby_bar_june = HighScoreUserDetail(many=True)
    baby_bar_oct = HighScoreUserDetail(many=True)
    pro_bar_feb = HighScoreUserDetail(many=True)
    pro_bar_july = HighScoreUserDetail(many=True)
