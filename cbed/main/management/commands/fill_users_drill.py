from django.core.management.base import BaseCommand

from cbed.authentication.serializers import fill_up_profile
from cbed.users.models import User


class Command(BaseCommand):
    help = 'Fill up user profiles with default drills'

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            fill_up_profile(user)
