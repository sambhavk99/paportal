# Generated by Django 2.0.10 on 2019-04-10 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0015_department_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='num',
            field=models.IntegerField(blank=True, null=True, verbose_name='Strength in on group'),
        ),
    ]