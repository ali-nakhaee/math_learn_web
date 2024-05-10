from django.contrib import admin

from .models import Practice, ConstantText, Answer, Help, Question, HomeWork, SampleHomeWork, SampleQuestion, HomeWorkAnswer, QuestionAnswer, Containing

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


class ContainingInline(admin.TabularInline):
    model = Containing
    extra = 0


@admin.register(HomeWork)
class HomeWorkAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'teacher']
    list_display_links = ['id', 'teacher']
    inlines = [ContainingInline,]

@admin.register(SampleHomeWork)
class SampleHomeWorkAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'base_homework']
    list_display_links = ['id', 'student', 'base_homework']

@admin.register(SampleQuestion)
class SampleQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'true_answer', 'base_question']
    list_display_links = ['id', 'base_question']

@admin.register(HomeWorkAnswer)
class HomeWorkAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'sample_homework', 'score', 'date_created']
    list_display_links = ['id', 'sample_homework']

@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'sample_question', 'answer', 'homework_answer', 'evaluation']
    list_display_links = ['id', 'sample_question', 'homework_answer']
