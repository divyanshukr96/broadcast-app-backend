# Generated by Django 2.2.5 on 2019-09-29 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0002_department_faculty_society_student_superuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faculty',
            name='dob',
            field=models.DateField(blank=True, null=True, verbose_name='Date of Birth'),
        ),
        migrations.AlterField(
            model_name='student',
            name='dob',
            field=models.DateField(blank=True, null=True, verbose_name='Date of Birth'),
        ),
    ]