from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        # Django 3.1 has no ModelAdmin.readonly_field_labels (that was added
        # in 3.2), so the label for the read-only "id" row is taken from the
        # form's Meta.labels. Without this the admin renders it as "ID".
        labels = {"id": _("User ID")}


class UserCreationForm(admin_forms.UserCreationForm):
    class Meta(admin_forms.UserCreationForm.Meta):
        model = User

        error_messages = {
            "username": {"unique": _("This username has already been taken.")}
        }
