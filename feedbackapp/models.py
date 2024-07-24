from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils import timezone

class User(AbstractUser):
    
    ROLES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLES)
    def save(self, *args, **kwargs):
        if self.password and not self.has_usable_password():
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class FailedLoginAttempts(models.Model):
    device_id = models.CharField(max_length=255, unique=True)
    attempts = models.PositiveBigIntegerField(default=0)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.device_id} - Attempts: {self.attempts}'

class Departments(models.Model):
    department_code = models.CharField(max_length=50, unique=True)
    department_name = models.CharField(max_length=250)
    department_logo = models.ImageField(upload_to='department_logo/', blank=True, null=True)
    
    def __str__(self):
        return self.department_name

class Faculty(User):
    faculty_id = models.CharField(max_length=20, unique=True)
    faculty_name = models.CharField(max_length=100)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE)
    faculty_image = models.ImageField(upload_to='faculty_images/', blank=True, null=True)
    def __str__(self):
        return self.faculty_name

class StudyingYear(models.Model):
    studying_year=models.PositiveIntegerField(unique=True,default=1)
    studying_year_name=models.CharField(max_length=40)

    def __str__(self):
        return self.studying_year_name
    
class Branches(models.Model):
    branch_code = models.CharField(max_length=10)
    studying_year = models.ForeignKey(StudyingYear, on_delete=models.CASCADE, null=True) 
    branch_name = models.CharField(max_length=250)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.branch_name
    class Meta:
        unique_together = ('branch_code', 'studying_year')

class Exam(models.Model):
    feedback_exam_code = models.CharField(max_length=10, unique=True,null=True)
    feedback_exam_name = models.CharField(max_length=50,null=True)
    max_options_per_question = models.PositiveIntegerField(
        default=2,
        help_text="Maximum number of options allowed per question in this exam."
    )
    options_limit_status = models.CharField(
        max_length=10, default='Not Changed', editable=False 
    ) 

    def __str__(self):
        return self.feedback_exam_name
    def save(self, *args, **kwargs):
        if self._state.adding or self.max_options_per_question != Exam.objects.get(pk=self.pk).max_options_per_question:
            self.options_limit_status = 'Changed' 
        else:
            self.options_limit_status = 'Not Changed'
        super().save(*args, **kwargs)
    @property
    def department(self):
        """Returns the department the faculty belongs to."""
        return self.faculty.department

    @property
    def faculty_name(self):
        """Returns the faculty's name or username if faculty name is not available."""
        return self.faculty.faculty_name if hasattr(self.faculty, 'faculty_name') else self.faculty.username

class Section(models.Model):
    section_number=models.CharField(max_length=20,default=1)
    section_name = models.CharField(max_length=50)
    studying_year = models.ForeignKey(StudyingYear, on_delete=models.CASCADE, null=True) 
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE,null=True)
    selected_exam=models.ForeignKey(Exam,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.section_name

    def clean(self):
        if self.branch:
            if self.branch.department != self.branch.department:
                raise ValidationError("Section must belong to the same department as its branch.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    class Meta:
        unique_together = ('section_number', 'studying_year', 'branch')
class Student(User):
    student_id = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=100)
    studying_year = models.ForeignKey(StudyingYear,on_delete=models.CASCADE)
    branch=models.ForeignKey(Branches,on_delete=models.CASCADE,null=True)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE)
    section = models.ForeignKey(Section,on_delete=models.CASCADE)

    def __str__(self):
        return self.student_name

class Subject(models.Model):
    subject_code = models.CharField(max_length=10)
    subject_name = models.CharField(max_length=100)
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'})
    studying_year = models.ForeignKey(StudyingYear, null=True, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branches, null=True, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, null=True, on_delete=models.CASCADE)
    midterm1_active = models.BooleanField(default=False)
    midterm2_active = models.BooleanField(default=False)
    midterm1_activated_at = models.DateTimeField(null=True, blank=True)
    midterm2_activated_at = models.DateTimeField(null=True, blank=True)
    midterm1_deactivate=models.DateTimeField(null=True,blank=True)
    midterm2_deactivate=models.DateTimeField(null=True,blank=True)
    def __str__(self):
        return self.subject_name
    class Meta:
        unique_together = ('section', 'studying_year', 'branch', 'subject_code')
    @property
    def department(self):
        """Returns the department the faculty belongs to."""
        return self.faculty.department
    def clean(self):
        super().clean()
        if self.midterm1_active and self.midterm1_activated_at:
            raise ValidationError("Midterm 1 has already been activated for this subject.")
        if self.midterm2_active and self.midterm2_activated_at:
            raise ValidationError("Midterm 2 has already been activated for this subject.")
        if self.midterm1_active and self.midterm2_active:
            raise ValidationError("Only one midterm feedback period can be active at a time.")

    def save(self, *args, **kwargs):
        if self.midterm1_active and not self.midterm1_activated_at:
            self.midterm1_activated_at = timezone.now()
        if self.midterm2_active and not self.midterm2_activated_at:
            self.midterm2_activated_at = timezone.now()

        super().save(*args, **kwargs)

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE,null=True)
    question_number = models.PositiveIntegerField(null=True)
    question_text = models.TextField(null=True)

    class Meta:
        unique_together = ('exam', 'question_number') 

    def __str__(self):
        return f"Q{self.question_number}. {self.question_text} (Exam: {self.exam.feedback_exam_code})"
class QuestionOption(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE,null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options',null=True)
    option_number = models.PositiveIntegerField(null=True) 
    option_text = models.CharField(max_length=255)
    option_score = models.PositiveIntegerField(null=True) 

    class Meta:
        unique_together = ('exam','question', 'option_number') 
    def __str__(self):
        return f"{self.option_text} ({self.option_score} points)"
    def clean(self):
        super().clean()

        if self.question.exam and self.question.options.count() >= self.question.exam.max_options_per_question:
            raise ValidationError(
                f"You can add only up to {self.question.exam.max_options_per_question} options for each question in this exam."
            )
class Feedback(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_feedbacks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='faculty_feedbacks')
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    options_mid_term_1=models.CharField(max_length=1000,null=True)
    options_mid_term_2=models.CharField(max_length=1000,null=True)
    comments_mid_term_1 = models.JSONField(blank=True,null=True) 
    comments_mid_term_2 = models.JSONField(blank=True,null=True) 
    mid_term = models.PositiveIntegerField(null=True, blank=True) 
    mid_term_1_rating=models.FloatField(null=True)
    mid_term_2_rating=models.FloatField(null=True)
    over_all_ratings = models.FloatField(null=True)
    created_at_mid_term_1 = models.DateTimeField(null=True)
    updated_at_mid_term_1 = models.DateTimeField(null=True)
    created_at_mid_term_2 = models.DateTimeField(null=True)
    updated_at_mid_term_2 = models.DateTimeField(null=True)
    is_submitted_mid_term_1 = models.BooleanField(default=False)
    is_submitted_mid_term_2 = models.BooleanField(default=False)

    @property
    def average_rating(self):
       return self.ratings if self.ratings else 0

    def __str__(self):
        return f'Feedback by {self.student} for {self.faculty} on {self.subject}'

    class Meta:
        unique_together = ('student', 'faculty', 'subject', 'section')
    @property
    def subjects_and_faculty(self):
        """Returns a list of dictionaries containing subject and faculty information for the student's section."""
        subjects_data = []
        subjects = Subject.objects.filter(section=self.section).values('subject_name', 'subject_code', 'faculty__faculty_name')
        for subject in subjects:
            subjects_data.append({
                'subject_name': subject['subject_name'],
                'subject_code': subject['subject_code'],
                'faculty_name': subject['faculty__faculty_name']
            })
        return subjects_data
    def save(self, *args, **kwargs):
        if self.mid_term_1_rating and self.mid_term_2_rating:
            self.over_all_ratings = (self.mid_term_1_rating + self.mid_term_2_rating) / 2
        super().save(*args, **kwargs)
