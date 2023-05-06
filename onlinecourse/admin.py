from django.contrib import admin
# <HINT> Import any new Models here
from .models import Course, Lesson, Instructor, Learner, Question, Choice

# <HINT> Register QuestionInline and ChoiceInline classes here
class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 3

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 3

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 3


# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class LessonAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ['title']
    list_filter = ['course__name']
    search_fields = ['title']

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_filter = ['lesson__course__name', 'lesson__title']
    search_fields = ['question_text']

class ChoiceAdmin(admin.ModelAdmin):
    list_filter = ['question__question_text','question__lesson__title', 'question__lesson__course__name']
    search_fields = ['choice_text']


# <HINT> Register Question and Choice models here
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)