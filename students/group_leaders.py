import os
from .models import Student, Choice, Group, Professor
from django.db.models import Sum


def group_leader():
    groups = (Professor.objects.filter(dept="Electronics and Communication Engineering").aggregate(num=Sum('group')))
    sums = groups['num']
    print(sums)
    student_list = Student.objects.all().order_by('-CPI')
    print(student_list)

    for i in range(sums):
        setattr(student_list[i], 'leader', True)
        student_list[i].save()
        print(student_list[i])
        print(student_list[i].leader)


def allot_mentor():
    g_leader = Student.objects.filter(leader=True).order_by('-CPI')
    for i in range(len(g_leader)):
        choice = Choice.objects.filter(student=g_leader[i]).order_by('priority')
        for j in range(len(choice)):
            if choice[j].professor.group_allotted < choice[j].professor.group:
                members = g_leader[i].group.user_set.all()
                for m in members:
                    setattr(m.student, 'mentor', choice[j])
                break



