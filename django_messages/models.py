from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from students.models import Student
import uuid
from .signals import *
from django.conf import settings
# Create your models here.
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class Message(models.Model):
    mid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    sender = models.ForeignKey(Student, related_name="sender", null=True, on_delete=models.SET_NULL)
    receiver = models.ForeignKey(Group, related_name="receiver", on_delete=models.CASCADE, verbose_name="Write message")
    subject = models.CharField(verbose_name="Subject", max_length=50, default='No Subject')
    content = models.CharField(verbose_name="Message", max_length=1500)
    created_at = models.DateTimeField(verbose_name="Time Created", default=timezone.now)
    seen = models.BooleanField(default=False, verbose_name="Message Seen")

    def __str__(self):
        return self.subject



