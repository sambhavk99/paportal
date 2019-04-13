from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Department)
admin.site.register(Professor)
admin.site.register(Student)
admin.site.register(Choice)
admin.site.register(GroupRequest)
admin.site.register(UserDirection)

