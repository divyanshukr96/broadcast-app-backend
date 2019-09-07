# Generated by Django 2.2.5 on 2019-09-07 21:37

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Notice', '__first__'),
        ('Users', '0003_auto_20190906_0253'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('Users.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='bookmark',
            field=models.ManyToManyField(db_table='bookmark', related_name='notices', to='Notice.Notice'),
        ),
        migrations.AddField(
            model_name='user',
            name='follow',
            field=models.ManyToManyField(related_name='_user_follow_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='interested',
            field=models.ManyToManyField(db_table='interested', related_name='interested', to='Notice.Notice'),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
