# Generated by Django 2.0.10 on 2019-04-10 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_messages', '0007_message_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='content',
            field=models.CharField(max_length=1500, verbose_name='Message'),
        ),
    ]
