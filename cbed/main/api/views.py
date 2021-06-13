from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from cbed.main.api.serializers import (
    LevelSerializer,
    LevelDetailSerializer,
    SectionDetailSerializer,
)
from cbed.main.models import Level, Section


class LevelViewSet(ReadOnlyModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LevelDetailSerializer
        return super().get_serializer_class()


class SectionViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionDetailSerializer
    permission_classes = [AllowAny]
