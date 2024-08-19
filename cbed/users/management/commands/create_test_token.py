import datetime

import jwt
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from cbed.users.models import User


class Command(BaseCommand):
    help = "Create test token"

    def handle(self, *args, **options):
        token = jwt.encode(
            {
                "token_type": "access",
                "exp": timezone.now() + datetime.timedelta(days=365 * 20),
                "jti": "jkfhb784g9728ubriu23y4928uk",
                "user_id": User.objects.get(username="free_tester").id,
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        print(token)
