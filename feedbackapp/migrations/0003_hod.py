# Generated by Django 5.0.7 on 2024-08-21 12:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedbackapp', '0002_exam_studyingyear_alter_feedback_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feedbackapp.departments')),
                ('faculty_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feedbackapp.faculty')),
            ],
        ),
    ]