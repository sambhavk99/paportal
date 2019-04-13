from django.db import models
from django.contrib.auth.models import User, Group
from django.db import models
from  django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.admin.widgets import AdminDateWidget
import uuid
from .signals import *
from notifications.models import Notification
# Create your models


class Professor(models.Model):
    DEP_CHOICES = (('Electronics and Communication Engineering', 'Electronics and Communication Engineering'),
                   ('Mechanical Engineering', 'Mechanical Engineering'),
                   ('Computer Science and Engineering', 'Computer Science and Engineering'),
                   ('Electrical Engineering', 'Electrical Engineering'),
                   ('Production and Industrial Engineering', 'Production and Industrial Engineering'),
                   ('Chemical Engineering', 'Chemical Engineering'),
                   ('Civil Engineering', 'Civil Engineering'),
                   ('Information Technology', 'Information Technology'),
                   ('Biotechnology', 'Biotechnology'))
    pid = models.IntegerField(verbose_name="Professor ID", default=0, primary_key=True)
    name = models.CharField(max_length=25, verbose_name="Name")
    desg = models.CharField(verbose_name="Designation", max_length=25)
    qual = models.CharField(verbose_name="Qualifications", max_length=50, blank=True)
    dept = models.CharField(verbose_name="Department", max_length=50, choices=DEP_CHOICES)
    aoi = models.CharField(verbose_name="Areas Of Interest", max_length=50)
    group = models.IntegerField(verbose_name="Number of Groups to be alloted", default=0)
    group_allotted = models.IntegerField(verbose_name="Groups alloted", default=0)

    def __str__(self):
        return self.name


class Student(models.Model):
    DEP_CHOICES = (('Electronics and Communication Engineering', 'Electronics and Communication Engineering'),
                   ('Mechanical Engineering', 'Mechanical Engineering'),
                   ('Computer Science and Engineering', 'Computer Science and Engineering'),
                   ('Electrical Engineering', 'Electrical Engineering'),
                   ('Production and Industrial Engineering', 'Production and Industrial Engineering'),
                   ('Chemical Engineering', 'Chemical Engineering'),
                   ('Civil Engineering', 'Civil Engineering'),
                   ('Information Technology', 'Information Technology'),
                   ('Biotechnology', 'Biotechnology'))
    CAT_CHOICES = (('OPEN', 'Open'), ('OPEN-PWD', 'OPEN-PWD'), ('OBC', 'OBC'), ('OBC-PWD', 'OBC-PWD'), ('SC', 'SC'),
                   ('SC-PWD', 'SC_PWD'), ('ST', 'ST'), ('ST-PWD', 'ST-PWD'))
    reg_no = models.OneToOneField(User, verbose_name="Registration Number", on_delete=models.CASCADE)
    Name = models.CharField(verbose_name="Student's Name", max_length=40)
    FName = models.CharField(verbose_name="Father's Name", max_length=60)
    Branch = models.CharField(verbose_name="Branch", max_length=100, choices=DEP_CHOICES)
    CPI = models.FloatField(verbose_name="CPI", default=0)
    DOB = models.DateField(verbose_name="Date of Birth")
    Category = models.CharField(verbose_name="Category", max_length=50, choices=CAT_CHOICES)
    Semester = models.IntegerField(verbose_name="Semester", default=8)
    group = models.ForeignKey(Group, verbose_name="Group", on_delete=models.CASCADE, null=True, blank=True)
    leader = models.BooleanField(verbose_name="Leader", default=False)
    preference = []
    mentor = models.ForeignKey(Professor, verbose_name="Mentor", on_delete=models.CASCADE, null=True, blank=True)
    choices_filled = models.BooleanField(verbose_name="Choices Filled", default=False)

    def add_preference(self, x):
        priority = Choice.objects.filter(student=self).count()
        pref = Choice.objects.create(student=self, professor=x, priority=priority+1)
        pref.save()

    def del_preference(self, x):
        pref = Choice.objects.filter(student=self, professor=x)[0]
        priority = pref.priority
        pref_list = Choice.objects.filter(student=self, priority__gt=priority)
        pref.delete()
        for preference in pref_list:
            preference.priority -= 1
            preference.save()

    def __str__(self):
        return self.Name


class Choice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    priority = models.IntegerField(verbose_name="Preference", default=0)

    def __str__(self):
        return self.professor.name


class GroupRequest(models.Model):
    rid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    sender = models.ForeignKey(Student, related_name="from_user", on_delete=models.CASCADE)
    receiver = models.ForeignKey(Student, related_name="to_user", on_delete=models.CASCADE, verbose_name="To",
                                 limit_choices_to={'group__isnull': True, 'leader': False})
    message = models.CharField(verbose_name="message", max_length=50, default="sent you a request to be in their group")
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "%s" % self.sender.Name

    def accept(self):
        self.sender.group.user_set.add(self.receiver.reg_no)
        f = self.receiver
        setattr(f, 'group', self.sender.group)
        f.save()
        self.delete()
        rec = GroupRequest.objects.filter(receiver=self.receiver)
        for r in rec:
            r.delete()
        request_accepted.send(
            sender=self,
            from_user=self.sender,
            to_user=self.receiver
        )

    def reject(self):
        self.delete()
        request_rejected.send(sender=self)

    def cancel(self):
        self.delete()
        request_canceled.send(sender=self)


class UserDirection(models.Model):
    user = models.OneToOneField(User, verbose_name="Superuser", on_delete=models.CASCADE, blank=True, null=True, limit_choices_to={'is_superuser':True})
    dep_login = models.BooleanField(default=False, verbose_name="Departmental Login Allowed")
    mentor_filling = models.BooleanField(default=False, verbose_name="Mentor Information Uploading Started")
    student_login = models.BooleanField(default=False, verbose_name="Student Login Allowed")
    student_filling = models.BooleanField(default=False, verbose_name="Student Information Uploading Started")
    Group_creation = models.BooleanField(default=False, verbose_name="Group Creation Allowed")
    Group_leaders = models.BooleanField(default=False, verbose_name="Group Leaders Created")
    send_request = models.BooleanField(default=False, verbose_name="Sending Requests Allowed")
    choice_filling = models.BooleanField(default=False, verbose_name="Choice Filling started")
    result_declared = models.BooleanField(default=False, verbose_name="Result Declared")

    def group_leader(self):
        DEP_CHOICES = ['Electronics and Communication Engineering',
                       'Mechanical Engineering', 'Computer Science and Engineering',
                       'Electrical Engineering',
                       'Production and Industrial Engineering', 'Chemical Engineering', 'Civil Engineering',
                       'Information Technology', 'Biotechnology']
        for dep in DEP_CHOICES:
            groups = (Professor.objects.filter(dept=dep).aggregate(num=Sum('group')))
            sum = groups['num']
            if sum is None:
                sum=0
            print(sum)
            student_list = list(Student.objects.all().order_by('-CPI'))
            print(student_list)

            for i in range(sum):
                setattr(student_list[i], 'leader', True)
                student_list[i].save()

    def allot_mentor(self):
        g_leader = list(Student.objects.filter(leader=True).order_by('-CPI'))
        for i in range(len(g_leader)):
            choice = list(Choice.objects.filter(student=g_leader[i]).order_by('priority'))
            for j in range(len(choice)):
                if choice[j].professor.group_allotted < choice[j].professor.group:
                    choice[j].professor.group_allotted += 1
                    choice[j].professor.save()
                    members = list(g_leader[i].group.user_set.all())
                    for m in members:
                        setattr(m.student, 'mentor', choice[j].professor)
                        m.student.save()
                    break

    def create(self):
        if self.student_filling is True:
            Notification.objects.get_or_create(heading="Student details updation has started",
                                               detail="Departments can now login to update the details of their students!")
        if self.mentor_filling is True:
            Notification.objects.get_or_create(heading="Mentor details updation has started",
                                               detail="Departments can now login to update and fill the details of mentors.")
        if self.Group_leaders is True:
            self.group_leader()
            Notification.objects.get_or_create(heading="Group leaders allotted",
                                               detail="Students can now login to see if they are the group leader.")
        if self.Group_creation is True:
            Notification.objects.get_or_create(heading="Group creation has started",
                                               detail="Group leaders can now login to create their group.")
        if self.send_request is True:
            Notification.objects.get_or_create(heading="Request Sending process has started",
                                               detail="Group leaders can now send requests to other students to add them to their group,Students can login to see if they have received any requests")
        if self.choice_filling is True:
            Notification.objects.get_or_create(heading="Choice filling has started",
                                               detail="Group Leaders can now fill their preferences for mentors for their projects.")
        if self.result_declared is True:
            self.allot_mentor()
            Notification.objects.get_or_create(heading="Results declared",
                                               detail="Students can now login to see who has been allotted as mentor for their group.")

    def __str__(self):
        return self.user.username


class Department(models.Model):
    DEP_CHOICES = (('Electronics and Communication Engineering', 'Electronics and Communication Engineering'),
                   ('Mechanical Engineering', 'Mechanical Engineering'),
                   ('Computer Science and Engineering', 'Computer Science and Engineering'),
                   ('Electrical Engineering', 'Electrical Engineering'),
                   ('Production and Industrial Engineering', 'Production and Industrial Engineering'),
                   ('Chemical Engineering', 'Chemical Engineering'),
                   ('Civil Engineering', 'Civil Engineering'),
                   ('Information Technology', 'Information Technology'),
                   ('Biotechnology', 'Biotechnology'))
    user = models.OneToOneField(User, verbose_name="Department username", on_delete=models.CASCADE)
    dep_name = models.CharField(verbose_name="Department Name", max_length=50, choices=DEP_CHOICES)
    num = models.IntegerField(verbose_name="Strength in on group", blank=True, null=True)

    def __str__(self):
        return self.dep_name

