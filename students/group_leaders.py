import os
from students.models import Student


def group_leader():
    student_list = Student.objects.all().order_by('CPI')

    for i in range(30):
        student_list[i].leader = True
        student_list[i].save()



