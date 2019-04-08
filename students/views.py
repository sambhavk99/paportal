# Create your views here.
from django.contrib.auth import login, authenticate
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from notifications.models import Notification
from django.contrib.auth.models import Group
from .models import *
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, HttpResponseRedirect, reverse
from django_messages.models import Message
from django.db import IntegrityError
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages


def base(request):
    user = User.objects.filter(is_superuser=True)[0]
    user.userdirection.create()
    num_of_prof = Professor.objects.all().count()
    notification_list = Notification.objects.order_by('-pub_date')
    superuser = User.objects.filter(is_superuser=True)[0]
    context = {
        'Total_Professors': num_of_prof,
        'Notification_list': notification_list,
        'superuser': superuser
    }
    return render(request, 'students/base.html', context=context)


@login_required(login_url='/accounts/login')
def index(request):
    """View function for home page of site."""
    num_of_prof = Professor.objects.all().count()
    notification_list = Notification.objects.order_by('-pub_date')
    grp = request.user.groups.all()
    avlbl_stu = Student.objects.filter(group__isnull=True, leader=False, Branch=request.user.student.Branch)
    msg = Message.objects.filter(receiver=request.user.student.group, seen=False).count()
    req = GroupRequest.objects.filter(receiver=request.user.student).count()
    already_sent = request.user.student.from_user.all()
    superuser = User.objects.filter(is_superuser=True)[0]
    as_req = []
    for reqs in already_sent:
        as_req.append(reqs.receiver)
    #print(already_sent)
    #print(as_req)
    if grp:
        g = grp[0]
    else:
        g = grp
    context = {
        'Total_Professors': num_of_prof,
        'Notification_list': notification_list,
        'Group': g,
        'All_Students': avlbl_stu,
        'Message_count': msg,
        'request_count': req,
        'already_sent': as_req,
        'superuser': superuser,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'students/home.html', context=context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'students/signup.html', {'form': form})


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Notification_list'] = Notification.objects.order_by('-pub_date')
        return context

@login_required(login_url='/accounts/login')
def group_view(request):
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            grp_form = form.save()
            grp, created = Group.objects.get_or_create(name=grp_form.grp_name)
            grp.user_set.add(request.user)
            f = request.user.student
            setattr(f, 'group', grp)
            f.save()
            return redirect('students:student_home')
    else:
        form = CreateGroupForm()
    ctx = {'Notification_list':Notification.objects.order_by('-pub_date'), 'form': form}
    return render(request, 'students/create_group.html', ctx)

@login_required(login_url='/accounts/login')
def confirm_choice(request):
    pref = request.user.student.preference
    for i in range(len(pref)):
        Choice.objects.get_or_create(student=request.user.student, professor=pref[i], priority=i+1)
    stu = request.user.student
    setattr(stu, 'choices_filled', True)
    stu.save()
    choices_filled = Choice.objects.filter(student=request.user.student)
    ctx = {'Choices_filled': choices_filled, 'Notification_list':Notification.objects.order_by('-pub_date')}
    return render(request, 'students/confirm.html', context=ctx)


@login_required(login_url='/accounts/login')
def home(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.sender = request.user.student
            req = req.save()
            form = RequestForm()
            return redirect('students:student_home')
    else:
        form = RequestForm()

    return render(request, 'students/request.html', {'form': form, 'Notification_list': Notification.objects.order_by('-pub_date')})


@login_required(login_url='/accounts/login')
def received(request):
    rec = GroupRequest.objects.filter(receiver=request.user.student)
    context = {
        'received':rec, 'Notification_list':Notification.objects.order_by('-pub_date'),
     }

    return render(request, 'students/received.html', context=context)


@login_required(login_url='/accounts/login')
def sent(request):
    snt = GroupRequest.objects.filter(sender=request.user.student)
    context = {'sent': snt, 'Notification_list':Notification.objects.order_by('-pub_date')}

    return render(request, 'students/sent.html', context=context)


class AcceptView(generic.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        req = get_object_or_404(GroupRequest, pk=kwargs['pk'])
        req.accept()
        return super().get_redirect_url(*args, **kwargs)


class RejectView(generic.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        req = get_object_or_404(GroupRequest, pk=kwargs['pk'])
        req.reject()
        return super().get_redirect_url(*args, **kwargs)


class CancelView(generic.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        req = get_object_or_404(GroupRequest, pk=kwargs['pk'])
        req.cancel()
        return super().get_redirect_url(*args, **kwargs)


@login_required(login_url='/accounts/login')
def index_view(request):
    if request.method == 'GET':  # If the form is submitted
        search_query = request.GET.get('search_box')
        if not search_query:
            prof = Professor.objects.filter(dept=request.user.student.Branch).order_by('name')
        else:
            prof = Professor.objects.filter(dept=request.user.student.Branch, aoi__contains=search_query).order_by('name')
        cf = request.user.student.choice_set.all().order_by('priority')
        prof_filled = []
        for e in cf:
            prof_filled.append(e.professor)
        context = {'Professor_list': prof, 'Notification_list':Notification.objects.order_by('-pub_date'),
                   'Filled_Choices': prof_filled, 'choices_filled': cf}
        return render(request, 'students/index.html', context=context)


class DetailView(generic.DetailView):
    model = Professor
    template_name = 'students/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Professor.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cf = self.request.user.student.choice_set.all().order_by('priority')
        prof_filled = []
        for e in cf:
            prof_filled.append(e.professor)
        prof = Professor.objects.filter(dept=self.request.user.student.Branch).order_by('name')
        context['Notification_list'] = Notification.objects.order_by('-pub_date')
        context['Professor_list'] = prof
        context['Filled_Choices'] = prof_filled
        context['choices_filled'] = cf
        return context


class AddView(generic.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'students:faculty_index'

    def get_redirect_url(self, *args, **kwargs):
        prof = get_object_or_404(Professor, pk=kwargs['pk'])
        self.request.user.student.add_preference(prof)
        self.request.user.student.save()
        return super().get_redirect_url(*args, **kwargs)


class RemoveView(generic.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        prof = get_object_or_404(Professor, pk=kwargs['pk'])
        self.request.user.student.del_preference(prof)
        self.request.user.student.save()
        return super().get_redirect_url(*args, **kwargs)


class DepLoginView(LoginView):
    authentication_form = DepartmentLoginForm
    redirect_field_name = 'students:dep_home'
    next = 'students:dep_home'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Notification_list'] = Notification.objects.order_by('-pub_date')
        context['next'] = self.next
        return context


class DepHomeView(generic.TemplateView):
    template_name = 'students/dep_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['Students_List'] = Student.objects.filter(Branch=user.department.dep_name)
        context['Professors_List'] = Professor.objects.filter(dept=user.department.dep_name)
        notification_list = Notification.objects.order_by('-pub_date')
        context['Notification_list'] = notification_list
        superuser = User.objects.filter(is_superuser=True)[0]
        context['superuser'] = superuser
        return context


def dep_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, 'Logged in successfully')
                return redirect('students:dep_home')
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'students/Dep_login.html', {})


@login_required(login_url='/accounts/login')
def faculty_view(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('students:add_mentor')
    else:
            form = FacultyForm()
    ctx = {'form': form, 'Notification_list': Notification.objects.order_by('-pub_date')}
    return render(request, 'students/faculty_form.html', ctx)


@login_required(login_url='/accounts/login')
def faculty_add_view(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            fac = form.save(commit=False)
            dep = User.objects.filter(username=request.user.username)[0]
            fac.dept = dep.department.dep_name
            fac = fac.save()
            return redirect('students:add_mentor')
    else:
        form = FacultyForm()
    ctx = {'form': form, 'Notification_list': Notification.objects.order_by('-pub_date')}
    return render(request, 'students/faculty_form.html', ctx)


@login_required(login_url='/accounts/login')
def student_view(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            stud = form.save(commit=False)
            username = form.cleaned_data.get('registration_no')
            users, created = User.objects.get_or_create(username=username, email=stud.email, password='qwertyuiop')
            stud.reg_no = users
            stud = stud.save()
            return redirect('students:dep_home')
    else:
            form = FacultyForm()
    ctx = {'form': form, 'Notification_list': Notification.objects.order_by('-pub_date')}

    return render(request, 'students/student_form.html', ctx)


@login_required(login_url='/accounts/login')
def student_add_view(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            stud = form.save(commit=False)
            username = form.cleaned_data.get('registration_no')
            email = form.cleaned_data.get('email')
            try:
                users = User.objects.create_user(username=username, email=email, password='qwertyuiop')
            except IntegrityError:
                return HttpResponse("Registration Number Already Exists!!!")
            stud.reg_no = users
            dep = User.objects.filter(username=request.user.username)[0]
            stud.Branch = dep.department.dep_name
            stud = stud.save()
            return redirect('students:add_student')
    else:
        form = StudentForm()
    ctx = {'form': form, 'Notification_list': Notification.objects.order_by('-pub_date')}

    return render(request, 'students/student_form.html', ctx)


class SendRequestView(generic.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        receiver = get_object_or_404(Student, pk=kwargs['pk'])
        GroupRequest.objects.create(sender=self.request.user.student, receiver=receiver)
        return super().get_redirect_url(*args, **kwargs)


class StudentUpdate(SuccessMessageMixin, generic.UpdateView):
    model = Student
    fields = ['reg_no', 'Name', 'FName', 'DOB', 'CPI', 'Category', 'Semester']
    template_name_suffix = '_form'
    success_url = '/accounts/department/home'
    success_message = "Student info was edited successfully!!"

    def get_success_message(self, cleaned_data):
        return self.success_message


class FacultyUpdate(generic.UpdateView):
    model = Professor
    fields = ['pid', 'name', 'desg', 'aoi', 'group']
    template_name = 'students/faculty_form.html'
    success_url = '/accounts/department/home'
    success_message = "Mentor info was edited successfully!!"

    def get_success_message(self, cleaned_data):
        return self.success_message
