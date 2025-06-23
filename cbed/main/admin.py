from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from cbed.main.models import Answer, Level, Question, Result, Section, Config, SubscriptionPlan


class SectionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Section
    show_change_link = True
    fields = ["name"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("level")


@admin.register(Level)
class LevelAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["name", "member_plan", "is_drills_and_videos", "modified"]
    list_filter = ["member_plan", "is_drills_and_videos"]
    inlines = [SectionInline]


class QuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Question
    show_change_link = True


@admin.register(Section)
class SectionAdmin(SortableAdminMixin, admin.ModelAdmin, DynamicArrayMixin):
    list_display = ["name", "member_plan", "level", "created", "modified"]
    list_filter = ["member_plan", "level"]
    search_fields = ["name"]
    inlines = [QuestionInline]


class AnswerInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Answer
    show_change_link = True


@admin.register(Question)
class QuestionAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["content", "section", "section__level", "created", "modified"]
    list_filter = ["section", "section__level"]
    search_fields = ["content"]
    inlines = [AnswerInline]

    def section__level(self, question: Question):
        return question.section.level


@admin.register(Answer)
class AnswerAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = [
        "content",
        "discussion",
        "is_correct",
        "question",
        "created",
        "modified",
    ]
    search_fields = ["content", "discussion"]


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ["user", "section", "correct", "total", "created", "modified"]
    list_filter = ["user", "section"]


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ("id","name","is_enable_login", "is_enable_delete_account", "is_default")

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price"]
    search_fields = ["name"]