from django.db.models import Sum
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from cbed.main.models import Level, Result, Section
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
        return self.queryset.filter(
            member_plan__lte=self.request.user.member_plan_simple
        )


class SectionViewSet(ReadOnlyModelViewSet):
    queryset = Section.objects.all().order_by("order").select_related("level")
    serializer_class = SectionSearchSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_fields = ["level"]
    search_fields = ("name", "level__name")
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return self.queryset.filter(
            member_plan__lte=self.request.user.member_plan_simple
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SectionDetailSerializer
        return super().get_serializer_class()

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

            user.available_sections.add(section)
            if result.grade >= 90:
                for level in Level.objects.filter(
                    order__gte=section.level.order
                ).order_by("order"):
                    for __section in Section.objects.filter(
                        level=level, order__gt=section.order
                    ).order_by("order"):
                        user.available_sections.add(__section)
                        break
                    else:
                        continue
                    break
            return JsonResponse(serializer.validated_data)
        else:
            return JsonResponse(serializer.errors)


class ScoreBoardView(RetrieveAPIView):
    queryset = User.objects.annotate(points=Sum("results__correct")).order_by("-points")
    serializer_class = HighScoreResultSerializer

    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {
                "baby_bar_june": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.BABY_BAR_JUNE
                    )[:4],
                    many=True,
                ).data,
                "baby_bar_oct": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.BABY_BAR_OCT
                    )[:4],
                    many=True,
                ).data,
                "pro_bar_feb": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.PRO_BAR_FEB
                    )[:4],
                    many=True,
                ).data,
                "pro_bar_july": HighScoreUserDetail(
                    instance=self.queryset.filter(
                        member_plan=MemberPlanChoices.PRO_BAR_JULY
                    )[:4],
                    many=True,
                ).data,
            }
        )
