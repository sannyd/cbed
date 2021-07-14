from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, DateTimeField, ManyToManyField, ImageField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for CBED."""

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    avatar = ImageField(null=True, blank=True)
    state = CharField(max_length=64, default="")
    membership = DateTimeField(default=timezone.now)
    available_sections = ManyToManyField("main.Section")
    first_name = None  # type: ignore
    last_name = None  # type: ignore
