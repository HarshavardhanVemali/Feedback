# Generated by Django 5.0.7 on 2024-08-21 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedbackapp', '0003_hod'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='hod',
            unique_together={('department', 'faculty_name')},
        ),
    ]
