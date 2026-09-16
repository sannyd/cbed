from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.fields import BooleanField

from cbed.main.consts import LevelNames
from cbed.main.models import Answer, Level, Question, Result, Section, SubscriptionPlan
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
        if (
            section.name == "Torts - Level 1"
            or section.name == "Level 1 - FL MCQ"
            or "Free" in section.level.name
        ):
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
        if section.level.name == LevelNames.AGENCY_LEVEL:
            if (
                current_user.current_agency_level
                and section.order <= current_user.current_agency_level.order
            ):
                return True
            return False
        if section.level.name == LevelNames.PARTNERSHIPS_LEVEL:
            if (
                current_user.current_partnerships_level
                and section.order <= current_user.current_partnerships_level.order
            ):
                return True
            return False

        if section.level.name == LevelNames.CORPS_LEVEL:
            if (
                current_user.current_corps_level
                and section.order <= current_user.current_corps_level.order
            ):
                return True
            return False

        if section.level.name == LevelNames.CONFLICTS_LEVEL:
            if (
                current_user.current_conflicts_level
                and section.order <= current_user.current_conflicts_level.order
            ):
                return True
            return False

        if section.level.name == LevelNames.FAM_LAW_LEVEL:
            if (
                current_user.current_fam_law_level
                and section.order <= current_user.current_fam_law_level.order
            ):
                return True
            return False

        if section.level.name == LevelNames.TRUSTS_LEVEL:
            if (
                current_user.current_trusts_level
                and section.order <= current_user.current_trusts_level.order
            ):
                return True
            return False

        if section.level.name == LevelNames.WILLS_LEVEL:
            if (
                current_user.current_wills_level
                and section.order <= current_user.current_wills_level.order
            ):
                return True
            return False

        if section.level.name == LevelNames.SEC_TRANS_LEVEL:
            if (
                current_user.current_sec_trans_level
                and section.order <= current_user.current_sec_trans_level.order
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
    # Per-section NextGen FK ids. The FK serializer natively exposes
    # `<field>_id` columns from the underlying integer columns, but only
    # when they're listed in `Meta.fields`. We list each explicitly here
    # so the iOS leaderboard reads them for the per-chip display text.
    #
    # Email & Zoom package flag, alias for `is_tutor`. The iOS app reads
    # this as `isEmailZoom` so the email-and-zoom tab can decide whether
    # to show the essay/mpt counters on Settings.
    is_email_zoom = serializers.BooleanField(source="is_tutor", read_only=True)

    # Resolved section names. Each reads its corresponding FK column
    # (e.g. `current_drafting_section`) and pulls the related Section's
    # `name` field (e.g. "Drafting Set 04") so the iOS leaderboard can
    # render the actual curriculum title under each NextGen chip instead
    # of the user's MBE level. Each is nullable so users who haven't
    # started a module just render "Not started" in the iOS UI.
    current_drafting_section_name = serializers.SerializerMethodField()
    current_counseling_section_name = serializers.SerializerMethodField()
    current_ng_spt_section_name = serializers.SerializerMethodField()
    current_ng_lrpt_section_name = serializers.SerializerMethodField()
    current_ng_mcq_1_choice_section_name = serializers.SerializerMethodField()
    current_ng_mcq_2_choice_section_name = serializers.SerializerMethodField()

    def _section_name(self, user, attr):
        section = getattr(user, attr, None)
        if section is None:
            return None
        # Section.__str__ is "name - level_name"; we want the bare name
        # so the iOS row reads "Drafting Set 04" rather than the full
        # verbose string.
        return getattr(section, "name", None) or str(section)

    def get_current_drafting_section_name(self, user):
        return self._section_name(user, "current_drafting_section")

    def get_current_counseling_section_name(self, user):
        return self._section_name(user, "current_counseling_section")

    def get_current_ng_spt_section_name(self, user):
        return self._section_name(user, "current_ng_spt_section")

    def get_current_ng_lrpt_section_name(self, user):
        return self._section_name(user, "current_ng_lrpt_section")

    def get_current_ng_mcq_1_choice_section_name(self, user):
        return self._section_name(user, "current_ng_mcq_1_choice_section")

    def get_current_ng_mcq_2_choice_section_name(self, user):
        return self._section_name(user, "current_ng_mcq_2_choice_section")

    class Meta:
        model = User
        fields = [
            "id", "name", "avatar", "points", "last_section_name",
            "essay_count", "mpt_count",
            "current_drafting_section_id", "current_counseling_section_id",
            "current_ng_spt_section_id", "current_ng_lrpt_section_id",
            "current_ng_mcq_1_choice_section_id", "current_ng_mcq_2_choice_section_id",
            "current_drafting_section_name", "current_counseling_section_name",
            "current_ng_spt_section_name", "current_ng_lrpt_section_name",
            "current_ng_mcq_1_choice_section_name", "current_ng_mcq_2_choice_section_name",
            "is_email_zoom",
        ]


class HighScoreResultSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    baby_bar_june = HighScoreUserDetail(many=True)
    baby_bar_oct = HighScoreUserDetail(many=True)
    pro_bar_feb = HighScoreUserDetail(many=True)
    pro_bar_july = HighScoreUserDetail(many=True)
    # New for iOS 11.1: Email & Zoom cohort reuses the legacy `is_tutor`
    # package flag. Excluded from member-plan buckets so the same users
    # don't appear twice.
    email_zoom = HighScoreUserDetail(many=True)
    tutor = HighScoreUserDetail(many=True)

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ["id", "name", "price"]