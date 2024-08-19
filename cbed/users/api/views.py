from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import ReceiptSerializer, UserInfoSerializer, UserUpdateInfoSerializer

User = get_user_model()


class UserViewSet(GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserInfoSerializer

    @action(detail=False, methods=["GET"])
    def info(self, request):
        serializer = UserInfoSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=["PATCH"], serializer_class=UserUpdateInfoSerializer)
    def update_info(self, request):
        serializer = UserUpdateInfoSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                status=status.HTTP_200_OK, data=UserInfoSerializer(request.user).data
            )
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class PurchaseView(CreateAPIView):
    serializer_class = ReceiptSerializer
