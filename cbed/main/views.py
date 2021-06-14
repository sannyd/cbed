from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ReadOnlyModelViewSet

from cbed.main.models import Level, Section, Result
from cbed.main.serializers import (
    LevelSerializer,
    LevelDetailSerializer,
    SectionDetailSerializer,
    SectionSearchSerializer,
    ResultSerializer,
)


class LevelViewSet(ReadOnlyModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LevelDetailSerializer
        return super().get_serializer_class()


class SectionViewSet(ReadOnlyModelViewSet):
    queryset = Section.objects.all().select_related("level")
    serializer_class = SectionSearchSerializer
    filter_backends = (SearchFilter,)
    search_fields = ("name", "level__name")
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SectionDetailSerializer
        return super().get_serializer_class()

    @action(detail=True, serializer_class=ResultSerializer, methods=["post"])
    def save_result(self, request, *args, **kwargs):
        section = self.get_object()
        user = self.request.user
        serializer = ResultSerializer(data=request.data)
        if serializer.is_valid():
            result, _ = Result.objects.get_or_create(section=section, user=user)
            result.correct = serializer.validated_data["correct"]
            result.total = serializer.validated_data["total"]
            result.save()
        return JsonResponse(serializer.validated_data)
