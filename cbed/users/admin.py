from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from cbed.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                    "is_tutor",
                    "is_tutor_for_bed",
                    "essay_count",
                    "mpt_count",
                    "member_plan",
                    "current_mbe_section",
                    "current_mixed_mbe_section",
                    "current_fl_mcq_drill",
                    "current_ca_mcq_drill",
                    "current_mpre_drill",
                    "current_ng_mcq_1_choice_section",
                    "current_ng_mcq_2_choice_section",
                    "current_agency_level",
                    "current_partnerships_level",
                    "current_corps_level",
                    "current_conflicts_level",
                    "current_fam_law_level",
                    "current_trusts_level",
                    "current_wills_level",
                    "current_sec_trans_level",
                    "is_unlock_essay_pt",
                )
            },
        ),
        (_("Personal info"), {"fields": ("name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = [
        "username",
        "is_active",
        "is_tutor",
        "is_tutor_for_bed",
        "member_plan",
        "membership",
        "last_login",
    ]
    list_filter = ["is_staff", "is_tutor", "is_tutor_for_bed", "member_plan", "is_superuser", "is_active", "groups"]

    search_fields = ["name", "email", "username"]
