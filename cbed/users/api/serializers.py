from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "avatar", "name", "state", "membership"]


class UserUpdateInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["avatar", "name", "state"]
