# Generated by Django 2.0.10 on 2019-04-04 19:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_auto_20190405_0047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdirection',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Superuser'),
        ),
    ]
