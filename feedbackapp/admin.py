from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import (
    FailedLoginAttempts, Branches, Faculty, Departments, Student, 
    Subject, Section, Feedback, Question, User,StudyingYear,Exam,QuestionOption
)

class FailedLoginAttemptsAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'attempts', 'is_active')
    list_filter = ('device_id', 'attempts', 'is_active')
    search_fields = ('device_id', 'attempts', 'is_active')

class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ('department_code', 'department_name', 'preview_image')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.department_logo:
            return mark_safe(f'<img src="{obj.department_logo.url}" style="max-width: 200px; max-height: 150px;">')
        else:
            return 'No image found'

    list_filter = ('department_code', 'department_name')
    search_fields = ('department_code', 'department_name')
class StudyingyearAdmin(admin.ModelAdmin):
    list_display=('studying_year','studying_year_name')
    search_fields=('studying_year','studying_year_name')
    list_filter=('studying_year','studying_year_name')

class BranchesAdmin(admin.ModelAdmin):
    list_display = ('branch_name', 'branch_code','department','studying_year')
    list_filter = ('branch_code', 'branch_name')
    search_fields = ('branch_code', 'branch_name')

class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'faculty_name', 'department', 'preview_image')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.faculty_image:
            return mark_safe(f'<img src="{obj.faculty_image.url}" style="max-width: 200px; max-height: 150px;">')
        else:
            return 'No image found'

    list_filter = ('faculty_id', 'faculty_name','department')
    search_fields = ('faculty_id', 'faculty_name', 'department__department_name')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'student_name','studying_year','department','branch','section')
    list_filter = ('department', 'section')
    search_fields = ('student_id', 'student_name', 'department__department_name', 'section__section_name')

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'subject_name','faculty','studying_year','branch')
    list_filter = ('subject_code', 'subject_name','faculty','studying_year','branch')
    search_fields = ('subject_code', 'subject_name','faculty','studying_year','branch')

class SectionAdmin(admin.ModelAdmin):
    list_display = ('section_number', 'section_name', 'branch', 'studying_year', 'get_department','selected_exam')
    list_filter = ('section_name', 'branch', 'branch__department')
    search_fields = ('section_name', 'branch__branch_name', 'branch__department__department_name','selected_exam')
    def get_department(self, obj):
        return obj.branch.department
    get_department.admin_order_field = 'branch__department'
    get_department.short_description = 'Department'

class FeedbackExamAdmin(admin.ModelAdmin):
    list_display=('feedback_exam_code','feedback_exam_name','max_options_per_question','options_limit_status')
    list_filter=('feedback_exam_code','feedback_exam_name','max_options_per_question','options_limit_status')
    search_fields=('feedback_exam_code','feedback_exam_name','max_options_per_question','options_limit_status')

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'faculty', 'subject', 'section','mid_term_1_rating','mid_term_2_rating','over_all_ratings','is_submitted_mid_term_1','is_submitted_mid_term_2')
    list_filter = ('student', 'faculty', 'subject', 'section')
    search_fields = ('student__username', 'faculty__username', 'subject__subject_name', 'section__section_name')
    
    def average_rating(self, obj):
        return obj.average_rating
    average_rating.short_description = 'Average Rating'

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam','question_number','question_text')
    search_fields = ('exam','question_number','question_text')

class QuestionOptionsAdmin(admin.ModelAdmin):
    list_display=('exam','option_number','option_text','option_score')
    search_display=('exam','option_number','option_text','option_score')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')
    list_filter = ('role',)
    search_fields = ('username', 'email', 'role')
    verbose_name = 'User'
    verbose_name_plural = 'Users'

admin.site.register(FailedLoginAttempts, FailedLoginAttemptsAdmin)
admin.site.register(Departments, DepartmentsAdmin)
admin.site.register(Branches, BranchesAdmin)
admin.site.register(StudyingYear,StudyingyearAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Exam,FeedbackExamAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionOption,QuestionOptionsAdmin)
admin.site.register(User, UserAdmin)
