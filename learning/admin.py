from django.contrib import admin

from .models import Practice, ConstantText, Answer, Help, Question

class ConstantTextInline(admin.TabularInline):
    model = ConstantText
    extra = 0

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class HelpInline(admin.TabularInline):
    model = Help
    extra = 0

@admin.register(Practice)
class PracticeAdmin(admin.ModelAdmin):
    list_display = ['id', 'teacher']
    list_display_links = ['id', 'teacher']
    inlines = [ConstantTextInline, AnswerInline, HelpInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'teacher']
    list_display_links = ['id', 'teacher']
