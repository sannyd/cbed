from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from cbed.main.models import Level, Section, Question, Answer


class SectionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Section
    show_change_link = True


@admin.register(Level)
class LevelAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["name", "created", "modified"]
    inlines = [SectionInline]


class QuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Question
    show_change_link = True


@admin.register(Section)
class SectionAdmin(SortableAdminMixin, admin.ModelAdmin, DynamicArrayMixin):
    list_display = ["name", "level", "created", "modified"]
    list_filter = ["level"]
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
    list_display = ["content", "discussion", "is_correct", "question", "created", "modified"]
    list_filter = ["question"]
    search_fields = ["content", "discussion"]
