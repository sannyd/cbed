from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    SignInSerializer,
    RegisterSerializer,
    SSOSerializer,
)


class SignInView(CreateAPIView):
    serializer_class = SignInSerializer
    permission_classes = [AllowAny]


class SSOView(CreateAPIView):
    serializer_class = SSOSerializer
    permission_classes = [AllowAny]


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class SignOutView(APIView):
    def post(self, request):
        return Response({"user": str(request.user)}, status=status.HTTP_202_ACCEPTED)
