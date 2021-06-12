from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin

from cbed.main.models import Level, Section, Question, Answer


class SectionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Section


@admin.register(Level)
class LevelAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["name", "created", "modified"]
    inlines = [SectionInline]


class QuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Question


@admin.register(Section)
class SectionAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["name", "level", "youtube_url", "pdf_url", "created", "modified"]
    list_filter = ["level"]
    inlines = [QuestionInline]


class AnswerInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Answer


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
