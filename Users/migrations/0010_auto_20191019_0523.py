# Generated by Django 2.2.5 on 2019-10-19 05:23

import Users.manager
import Users.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0009_auto_20191015_2345'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacultyUser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('Users.user',),
            managers=[
                ('objects', Users.manager.UserManager()),
            ],
        ),
        migrations.RenameField(
            model_name='faculty',
            old_name='sex',
            new_name='gender',
        ),
        migrations.AddField(
            model_name='society',
            name='convener',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and underscore only.', max_length=150, null=True, unique=True, validators=[Users.validators.UsernameValidator()], verbose_name='username'),
        ),
    ]
