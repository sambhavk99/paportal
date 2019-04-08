from django.db import models
import uuid
from django.utils import timezone
# Create your models here.


class Notification(models.Model):
    nid = models.UUIDField(verbose_name="Notification ID", default=uuid.uuid4, unique=True, primary_key=True )
    heading = models.CharField(verbose_name="Notification Heading", max_length=40)
    detail = models.CharField(verbose_name="Details", max_length=150)
    pub_date = models.DateTimeField(verbose_name="Date Published", default=timezone.now)

    def __str__(self):
        return self.heading

