from django.http import JsonResponse
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from cbed.main.consts import LevelNames
from cbed.main.models import Level, Question, Result, Section, Config, SubscriptionPlan
from cbed.main.serializers import (
    HighScoreResultSerializer,
    HighScoreUserDetail,
    LevelSerializer,
    ResultSerializer,
    SectionDetailSerializer,
    SectionSearchSerializer, SubscriptionPlanSerializer,
)
from cbed.transactions.enums import MemberPlanChoices
from cbed.users.models import User


class LevelViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(
                member_plan__lte=self.request.user.member_plan_simple
            )
        return self.queryset


class SectionViewSet(ReadOnlyModelViewSet):
    queryset = Section.objects.all().order_by("order").select_related("level")
    serializer_class = SectionSearchSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_fields = ["level"]
    search_fields = ("name", "level__name")
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(
                member_plan__lte=self.request.user.member_plan_simple
            )
        return self.queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SectionDetailSerializer
        return super().get_serializer_class()

    @action(detail=False, url_path="essays")
    def search_essay(self, request, *args, **kwargs):
        if search := self.request.GET.get("search", "").strip():
            sections = set(
                Question.objects.filter(content__contains=search).values_list(
                    "section", flat=True
                )
            )
            queryset = self.queryset.filter(id__in=sections)
            if level_id := self.request.GET.get("level", "").strip():
                queryset = queryset.filter(level=level_id)
        else:
            queryset = self.queryset.none()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, serializer_class=ResultSerializer, methods=["post"])
    def save_result(self, request, *args, **kwargs):
        section = self.get_object()
        user: User = self.request.user
        serializer = ResultSerializer(data=request.data)
        if serializer.is_valid():
            result, _ = Result.objects.get_or_create(section=section, user=user)
            result.correct = serializer.validated_data["correct"]
            result.total = serializer.validated_data["total"]
            result.save()

            mbe_level = Level.objects.filter(name=LevelNames.MBE_LEVEL_DRILLS).first()

            if mbe_level and mbe_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=mbe_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_mbe_section is None or (
                        next_section
                        and user.current_mbe_section.order < next_section.order
                    ):
                        user.current_mbe_section = next_section
                        user.save()

                if result.grade < 30:
                    start_level_section = (
                        Section.objects.filter(
                            level=mbe_level,
                            order__lt=section.order,
                        )
                        .order_by("-order")
                        .first()
                    )
                    if start_level_section:
                        user.current_mbe_section = start_level_section
                        user.save()

                section_tort_level_4 = Section.objects.filter(
                    name="Torts - Level 4", level__name=LevelNames.MBE_LEVEL_DRILLS
                ).first()
                if (
                    section_tort_level_4
                    and user.current_mbe_section
                    and user.current_mbe_section.order >= section_tort_level_4.order
                ):
                    user.is_unlock_essay_pt = True
                    user.save()
            mcq_level = Level.objects.filter(name=LevelNames.FL_MCQ_DRILLS).first()

            if mcq_level and mcq_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=mcq_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_fl_mcq_drill is None or (
                        next_section
                        and user.current_fl_mcq_drill.order < next_section.order
                    ):
                        user.current_fl_mcq_drill = next_section
                        user.save()

                if result.grade < 30:
                    start_level_section = (
                        Section.objects.filter(
                            level=mcq_level,
                            order__lt=section.order,
                        )
                        .order_by("-order")
                        .first()
                    )
                    if start_level_section:
                        user.current_fl_mcq_drill = start_level_section
                        user.save()
            ca_level = Level.objects.filter(name=LevelNames.CA_MCQ_DRILLS).first()
            if ca_level and ca_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=ca_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_ca_mcq_drill is None or (
                        next_section
                        and user.current_ca_mcq_drill.order < next_section.order
                    ):
                        user.current_ca_mcq_drill = next_section
                        user.save()
                if result.grade < 30:
                    start_level_section = (
                        Section.objects.filter(
                            level=ca_level,
                            order__lt=section.order,
                        )
                        .order_by("-order")
                        .first()
                    )
                    if start_level_section:
                        user.current_ca_mcq_drill = start_level_section
                        user.save()

            ng_level = Level.objects.filter(name=LevelNames.NG_MCQ_1_CHOICE).first()
            if ng_level and ng_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=ng_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_ng_mcq_1_choice_section is None or (
                        next_section
                        and user.current_ng_mcq_1_choice_section.order < next_section.order
                    ):
                        user.current_ng_mcq_1_choice_section = next_section
                        user.save()

                if result.grade < 30:
                    start_level_section = (
                        Section.objects.filter(
                            level=ng_level,
                            order__lt=section.order,
                        )
                        .order_by("-order")
                        .first()
                    )
                    if start_level_section:
                        user.current_ng_mcq_1_choice_section = start_level_section
                        user.save()
            # MPRE_DRILLS
            mpre_level = Level.objects.filter(name=LevelNames.MPRE_DRILLS).first()
            if mpre_level and mpre_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=mpre_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_mpre_drill is None or (
                        next_section
                        and user.current_mpre_drill.order < next_section.order
                    ):
                        user.current_mpre_drill = next_section
                        user.save()

            # AGENCY_LEVEL
            agency_level = Level.objects.filter(name=LevelNames.AGENCY_LEVEL).first()
            if agency_level and agency_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=agency_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_agency_level is None or (
                        next_section
                        and user.current_agency_level.order < next_section.order
                    ):
                        user.current_agency_level = next_section
                        user.save()

            # PARTNERSHIPS_LEVEL
            partnerships_level = Level.objects.filter(
                name=LevelNames.PARTNERSHIPS_LEVEL
            ).first()
            if partnerships_level and partnerships_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=partnerships_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_partnerships_level is None or (
                        next_section
                        and user.current_partnerships_level.order < next_section.order
                    ):
                        user.current_partnerships_level = next_section
                        user.save()

            # CORPS_LEVEL
            corps_level = Level.objects.filter(name=LevelNames.CORPS_LEVEL).first()
            if corps_level and corps_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=corps_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_corps_level is None or (
                        next_section
                        and user.current_corps_level.order < next_section.order
                    ):
                        user.current_corps_level = next_section
                        user.save()

            # CONFLICTS_LEVEL
            conflicts_level = Level.objects.filter(
                name=LevelNames.CONFLICTS_LEVEL
            ).first()
            if conflicts_level and conflicts_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=conflicts_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_conflicts_level is None or (
                        next_section
                        and user.current_conflicts_level.order < next_section.order
                    ):
                        user.current_conflicts_level = next_section
                        user.save()

            # FAM_LAW_LEVEL
            fam_law_level = Level.objects.filter(name=LevelNames.FAM_LAW_LEVEL).first()
            if fam_law_level and fam_law_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=fam_law_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_fam_law_level is None or (
                        next_section
                        and user.current_fam_law_level.order < next_section.order
                    ):
                        user.current_fam_law_level = next_section
                        user.save()

            # TRUSTS_LEVEL
            trusts_level = Level.objects.filter(name=LevelNames.TRUSTS_LEVEL).first()
            if trusts_level and trusts_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=trusts_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_trusts_level is None or (
                        next_section
                        and user.current_trusts_level.order < next_section.order
                    ):
                        user.current_trusts_level = next_section
                        user.save()

            # WILLS_LEVEL
            wills_level = Level.objects.filter(name=LevelNames.WILLS_LEVEL).first()
            if wills_level and wills_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=wills_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_wills_level is None or (
                        next_section
                        and user.current_wills_level.order < next_section.order
                    ):
                        user.current_wills_level = next_section
                        user.save()

            # SEC_TRANS_LEVEL
            sec_trans_level = Level.objects.filter(
                name=LevelNames.SEC_TRANS_LEVEL
            ).first()
            if sec_trans_level and sec_trans_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=sec_trans_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_sec_trans_level is None or (
                        next_section
                        and user.current_sec_trans_level.order < next_section.order
                    ):
                        user.current_sec_trans_level = next_section
                        user.save()

            # DRAFTING_SETS (level 31)
            drafting_level = Level.objects.filter(name=LevelNames.DRAFTING_SETS).first()
            if drafting_level and drafting_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=drafting_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_drafting_section is None or (
                        next_section
                        and user.current_drafting_section.order < next_section.order
                    ):
                        user.current_drafting_section = next_section
                        user.save()

                if result.grade < 30:
                    start_level_section = (
                        Section.objects.filter(
                            level=drafting_level,
                            order__lt=section.order,
                        )
                        .order_by("-order")
                        .first()
                    )
                    if start_level_section:
                        user.current_drafting_section = start_level_section
                        user.save()

            # COUNSELING_SETS (level 33)
            counseling_level = Level.objects.filter(name=LevelNames.COUNSELING_SETS).first()
            if counseling_level and counseling_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=counseling_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_counseling_section is None or (
                        next_section
                        and user.current_counseling_section.order < next_section.order
                    ):
                        user.current_counseling_section = next_section
                        user.save()

                if result.grade < 30:
                    start_level_section = (
                        Section.objects.filter(
                            level=counseling_level,
                            order__lt=section.order,
                        )
                        .order_by("-order")
                        .first()
                    )
                    if start_level_section:
                        user.current_counseling_section = start_level_section
                        user.save()

            # STANDARD_PERF_TASKS (level 34)
            spt_level = Level.objects.filter(name=LevelNames.STANDARD_PERF_TASKS).first()
            if spt_level and spt_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=spt_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_ng_spt_section is None or (
                        next_section
                        and user.current_ng_spt_section.order < next_section.order
                    ):
                        user.current_ng_spt_section = next_section
                        user.save()

                if result.grade < 30:
                    start_level_section = (
                        Section.objects.filter(
                            level=spt_level,
                            order__lt=section.order,
                        )
                        .order_by("-order")
                        .first()
                    )
                    if start_level_section:
                        user.current_ng_spt_section = start_level_section
                        user.save()

            # LRPTS (level 35)
            lrpt_level = Level.objects.filter(name=LevelNames.LRPTS).first()
            if lrpt_level and lrpt_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=lrpt_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_ng_lrpt_section is None or (
                        next_section
                        and user.current_ng_lrpt_section.order < next_section.order
                    ):
                        user.current_ng_lrpt_section = next_section
                        user.save()

                if result.grade < 30:
                    start_level_section = (
                        Section.objects.filter(
                            level=lrpt_level,
                            order__lt=section.order,
                        )
                        .order_by("-order")
                        .first()
                    )
                    if start_level_section:
                        user.current_ng_lrpt_section = start_level_section
                        user.save()

            # MIXED_MBE_SETS (level 40)
            mixed_mbe_level = Level.objects.filter(name=LevelNames.MIXED_MBE_SETS).first()
            if mixed_mbe_level and mixed_mbe_level == section.level:
                if result.grade >= 90:
                    next_section = (
                        self.get_queryset()
                        .filter(level=mixed_mbe_level, order__gt=section.order)
                        .order_by("order")
                        .first()
                    )
                    if user.current_mixed_mbe_section is None or (
                        next_section
                        and user.current_mixed_mbe_section.order < next_section.order
                    ):
                        user.current_mixed_mbe_section = next_section
                        user.save()

                if result.grade < 30:
                    start_level_section = (
                        Section.objects.filter(
                            level=mixed_mbe_level,
                            order__lt=section.order,
                        )
                        .order_by("-order")
                        .first()
                    )
                    if start_level_section:
                        user.current_mixed_mbe_section = start_level_section
                        user.save()
            return JsonResponse(serializer.validated_data)
        else:
            return JsonResponse(serializer.errors)


class ScoreBoardV110View(RetrieveAPIView):
    """iOS 11.0 scoreboard (legacy). Served at `/api/scoreboard`.

    SHIPPED in iOS 11.0 — currently live in the App Store. Backed by the
    legacy `is_tutor` flag (NOT the newer `is_tutor_for_bed`). Cannot be
    removed until the iOS 11.0 install base drops to zero.

    Pair: iOS 11.0 app → ScoreboardRouter.swift path "/scoreboard"
          → this view → uses `Q(is_tutor=True)`
    """
    queryset = User.objects.order_by("-current_mbe_section__order")
    serializer_class = HighScoreResultSerializer

    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {
                "baby_bar_june": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.BABY_BAR_JUNE, is_tutor=False,
                    ),
                    many=True,
                ).data,
                "baby_bar_oct": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.BABY_BAR_OCT, is_tutor=False,
                    ),
                    many=True,
                ).data,
                "pro_bar_feb": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.PRO_BAR_FEB, is_tutor=False,
                    ),
                    many=True,
                ).data,
                "pro_bar_july": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.PRO_BAR_JULY, is_tutor=False,
                    ),
                    many=True,
                ).data,
                "tutor": HighScoreUserDetail(
                    instance=self.queryset.filter(
                         is_tutor=True
                    ),
                    many=True,
                ).data,
            }
        )


class ScoreBoardV111View(RetrieveAPIView):
    """iOS 11.1 scoreboard. Served at `/api/scoreboard-111`.

    New with iOS 11.1 release. Backed by the canonical tutor flag
    `is_tutor_for_bed` (instead of the legacy `is_tutor`), so students
    who happen to have `is_tutor=True` (e.g. as part of a tutoring
    package) no longer appear in the `tutor` bucket or in any student
    leaderboard rank.

    Pair: iOS 11.1 app → ScoreboardRouter.swift path "/scoreboard-111"
          → this view → uses `Q(is_tutor_for_bed=True)` for tutors
          and `Q(is_tutor_for_bed=False)` for student buckets

    Differences from `ScoreBoardV110View` (iOS 11.0 legacy):
    - Each leaderboard bucket excludes users flagged `is_tutor_for_bed=True`,
      NOT just `is_tutor=False`. This ensures the new tutor flag (which can
      be true even when `is_tutor` is false) keeps tutors out of rankings.
    - The `tutor` bucket now includes only users with `is_tutor_for_bed=True`
      (4 users today: San, Crystal, Niya, Mentor Ariana). The legacy
      `is_tutor` flag is ignored here to give the iOS Tutors sheet a
      single source of truth.
    """
    queryset = User.objects.order_by("-current_mbe_section__order")
    serializer_class = HighScoreResultSerializer

    def get(self, request, *args, **kwargs):
        not_a_tutor = Q(is_tutor_for_bed=False)
        return JsonResponse(
            {
                "baby_bar_june": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.BABY_BAR_JUNE,
                        is_tutor_for_bed=False,
                    ),
                    many=True,
                ).data,
                "baby_bar_oct": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.BABY_BAR_OCT,
                        is_tutor_for_bed=False,
                    ),
                    many=True,
                ).data,
                "pro_bar_feb": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.PRO_BAR_FEB,
                        is_tutor_for_bed=False,
                    ),
                    many=True,
                ).data,
                "pro_bar_july": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.PRO_BAR_JULY,
                        is_tutor_for_bed=False,
                    ),
                    many=True,
                ).data,
                "tutor": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        Q(is_tutor_for_bed=True)
                    ),
                    many=True,
                ).data,
            }
        )


class GlobalConfigView(RetrieveAPIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        default_config = Config.objects.filter(
            is_default=True
        ).first()
        if not default_config:
            default_config = Config.objects.create(
                name="default config",
                is_enable_login=True,
                is_enable_delete_account=True,
                is_default=True,
            )
        return JsonResponse(
            {
                "name": default_config.name,
                "is_enable_login": default_config.is_enable_login,
                "is_enable_delete_account": default_config.is_enable_delete_account,
            }
        )
class AllGlobalConfigView(RetrieveAPIView):
    permission_classes = []
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        queryset = Config.objects.all()
        return JsonResponse([
            {
                "name": config.name,
                "is_enable_login": config.is_enable_login,
                "is_enable_delete_account": config.is_enable_delete_account,
                "is_default": config.is_default,
            }
            for config in queryset
        ], safe=False
        )


class SubscriptionPlanViewSet(ReadOnlyModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = []
    authentication_classes = []
