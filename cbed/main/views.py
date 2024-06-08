from django.db.models import Sum
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from cbed.main.consts import LevelNames
from cbed.main.models import Level, Question, Result, Section
from cbed.main.serializers import (
    HighScoreResultSerializer,
    HighScoreUserDetail,
    LevelSerializer,
    ResultSerializer,
    SectionDetailSerializer,
    SectionSearchSerializer,
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
            queryset = self.queryset.filter(
                id__in=sections
            )
            if level_id := self.request.GET.get("level","").strip():
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

                # section_tort_level_4 = Section.objects.filter(
                #     name="Torts - Level 4", level__name=LevelNames.MBE_LEVEL_DRILLS
                # ).first()
                # if (
                #     section_tort_level_4
                #     and user.current_mbe_section
                #     and user.current_mbe_section.order >= section_tort_level_4.order
                # ):
                #     user.is_unlock_essay_pt = True
                #     user.save()
            return JsonResponse(serializer.validated_data)
        else:
            return JsonResponse(serializer.errors)


class ScoreBoardView(RetrieveAPIView):
    queryset = User.objects.order_by("-current_mbe_section__order")
    serializer_class = HighScoreResultSerializer

    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {
                "baby_bar_june": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.BABY_BAR_JUNE
                    ),
                    many=True,
                ).data,
                "baby_bar_oct": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.BABY_BAR_OCT
                    ),
                    many=True,
                ).data,
                "pro_bar_feb": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.PRO_BAR_FEB
                    ),
                    many=True,
                ).data,
                "pro_bar_july": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.PRO_BAR_JULY
                    ),
                    many=True,
                ).data,
            }
        )
