from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ReadOnlyModelViewSet

from cbed.main.api.serializers import (
    LevelSerializer,
    LevelDetailSerializer,
    SectionDetailSerializer, SectionSearchSerializer,
)
from cbed.main.models import Level, Section


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
    search_fields = ('name', "level__name")
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SectionDetailSerializer
        return super().get_serializer_class()
