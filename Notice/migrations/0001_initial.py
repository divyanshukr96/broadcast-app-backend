# Generated by Django 2.2.5 on 2019-09-07 21:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('name', models.TextField(max_length=200)),
                ('short_name', models.TextField(max_length=10)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('public_notice', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=191)),
                ('description', models.TextField(blank=True)),
                ('date', models.DateField(blank=True)),
                ('time', models.TimeField(blank=True)),
                ('venue', models.CharField(blank=True, max_length=100)),
                ('department', models.ManyToManyField(blank=True, to='Notice.Department')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('viewed', models.ManyToManyField(blank=True, db_table='viewed', related_name='viewed', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]