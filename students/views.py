# Create your views here.
from django.contrib.auth import login, authenticate
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from datetime import timedelta
from .models import *
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django_messages.models import Message
from django.db import IntegrityError
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

'''BASE SITE VIEW'''


def base(request):
    num_of_prof = Professor.objects.all().count()
    notification_list = Notification.objects.order_by('-pub_date')
    new = timezone.now() - timedelta(days=2)
    superuser = User.objects.filter(is_superuser=True)[0]
    slform = CustomAuthenticationForm
    dlform = DepartmentLoginForm

    try:
        req = GroupRequest.objects.filter(receiver=request.user.student).count()
    except AttributeError:
        req = 0
    context = {
        'Total_Professors': num_of_prof,
        'Notification_list': notification_list,
        'superuser': superuser,
        'Dlform': dlform,
        'Slform': slform,
        'new': new,
        'request_count': req
    }

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, 'Logged in successfully')
                try:
                    u = user.student
                except Student.DoesNotExist:
                    u = None
                if u is None:
                    return redirect('students:dep_home')
                return redirect('students:student_home')
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            messages.warning(request, "Invalid details")
            return redirect('home')

    return render(request, 'students/base.html', context=context)


'''STUDENT HOME VIEW'''


@login_required(login_url='/accounts/login')
def index(request):
    """View function for home page of site."""
    num_of_prof = Professor.objects.all().count()
    notification_list = Notification.objects.order_by('-pub_date')
    grp = request.user.groups.all()
    avlbl_stu = Student.objects.filter(group__isnull=True, leader=False, Branch=request.user.student.Branch)
    try:
        dep = Department.objects.get(dep_name=request.user.student.Branch)
        num = dep.num
    except Department.DoesNotExist:
        num = 0

    msg = Message.objects.filter(receiver=request.user.student.group, seen=False).count()
    rec = list(GroupRequest.objects.filter(receiver=request.user.student))
    for r in rec:
        if r.sender.group.user_set.all().count() >= num:
            r.delete()
    req = GroupRequest.objects.filter(receiver=request.user.student).count()
    already_sent = request.user.student.from_user.all()
    superuser = User.objects.filter(is_superuser=True)[0]
    as_req = []
    try:
        members = list(request.user.student.group.user_set.all())
    except AttributeError:
        members = None
    try:
        c = request.user.student.group.user_set.all().count()
    except AttributeError:
        c = 0
    for reqs in already_sent:
        as_req.append(reqs.receiver)
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
        'members': members,
        'count': c,
        'max': num


    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'students/home.html', context=context)


'''SIGNUP VIEW, NOT IN WORK'''


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


'''LOGIN USING URL, NOT IN WORK'''


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Notification_list'] = Notification.objects.order_by('-pub_date')
        return context


'''CREATE GROUP VIEW'''


@login_required(login_url='/accounts/login')
def group_view(request):
    if request.user.student.leader and not request.user.student.group:
        if request.method == 'POST':
            form = CreateGroupForm(request.POST)
            if form.is_valid():
                grp_form = form.cleaned_data
                try:
                    grp = Group.objects.get(name=grp_form.get('name'))
                except Group.DoesNotExist:
                    grp = None

                if grp is None:
                    grp, created = Group.objects.get_or_create(name=grp_form.get('name'))
                else:
                    messages.error(request, "Group name already exists, try another name!!")
                    return redirect('students:group_creation')
                grp.user_set.add(request.user)
                f = request.user.student
                setattr(f, 'group', grp)
                f.save()
                return redirect('students:student_home')
        else:
            form = CreateGroupForm
        ctx = {'Notification_list':Notification.objects.order_by('-pub_date'), 'form': form}
        return render(request, 'students/create_group.html', ctx)
    else:
        messages.warning(request, "Invalid attempt! Cannot create Group")
        return redirect('students:student_home')


'''CHOICE FILLING CONFIRMATION VIEW, NOT IN USE'''


@login_required(login_url='/accounts/login')
def confirm_choice(request):
    pref = request.user.student.preference
    for i in range(len(pref)):
        Choice.objects.get_or_create(student=request.user.student, professor=pref[i], priority=i+1)
    stu = request.user.student
    setattr(stu, 'choices_filled', True)
    stu.save()
    choices_filled = Choice.objects.filter(student=request.user.student)
    try:
        members = list(request.user.student.group.user_set.all())
    except AttributeError:
        members = None
    ctx = {'Choices_filled': choices_filled, 'Notification_list': Notification.objects.order_by('-pub_date'),
           'members': members}
    return render(request, 'students/confirm.html', context=ctx)


'''SEND REQUEST USING FORM, NOT IN WORK'''


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


'''RECEIVED REQUESTS'''


@login_required(login_url='/accounts/login')
def received(request):
    try:
        dep = Department.objects.get(dep_name=request.user.student.Branch)
        num = dep.num
    except Department.DoesNotExist:
        num = 0
    if not request.user.student.leader and not request.user.student.group:
        rec = list(GroupRequest.objects.filter(receiver=request.user.student))
        req = GroupRequest.objects.filter(receiver=request.user.student).count()
        try:
            members = list(request.user.student.group.user_set.all())
        except AttributeError:
            members = None
        context = {
            'received': rec, 'Notification_list': Notification.objects.order_by('-pub_date'), 'members': members,
            'request_count': req
        }

        return render(request, 'students/received.html', context=context)
    else:
        messages.warning(request, "Unauthorized attempt to access page! Access denied!!")
        return redirect('students:student_home')


'''SENT REQUEST VIEW'''


@login_required(login_url='/accounts/login')
def sent(request):
    if request.user.student.leader and request.user.student.group:
        snt = GroupRequest.objects.filter(sender=request.user.student)
        try:
            members = list(request.user.student.group.user_set.all())
        except AttributeError:
            members = None
        context = {'sent': snt, 'Notification_list': Notification.objects.order_by('-pub_date'), 'members':members}

        return render(request, 'students/sent.html', context=context)
    else:
        messages.warning(request, "Unauthorized attempt to access page! Access denied!!")
        return redirect('students:student_home')


'''ACCEPT REQUEST VIEW'''


class AcceptView(generic.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'students:student_home'

    def get_redirect_url(self, *args, **kwargs):
        req = get_object_or_404(GroupRequest, pk=kwargs['pk'])
        req.accept()
        messages.success(self.request, "Request accepted")
        return super().get_redirect_url(*args, **kwargs)


'''REJECT REQUEST VIEW'''


class RejectView(generic.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'students:received'

    def get_redirect_url(self, *args, **kwargs):
        req = get_object_or_404(GroupRequest, pk=kwargs['pk'])
        req.reject()
        messages.success(self.request, "Request rejected!")
        return super().get_redirect_url(*args, **kwargs)


'''CANCEL REQUEST VIEW'''


class CancelView(SuccessMessageMixin, generic.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'students:sent'
    success_message = "Request Cancelled!"

    def get_success_message(self, cleaned_data):
        return self.success_message

    def get_redirect_url(self, *args, **kwargs):
        req = get_object_or_404(GroupRequest, pk=kwargs['pk'])
        req.cancel()
        messages.success(self.request, "Request Cancelled!")
        return super().get_redirect_url(*args, **kwargs)


'''CHOICE FILLING INDEX VIEW'''


@login_required(login_url='/accounts/login')
def index_view(request):
    prof = Professor.objects.filter(dept=request.user.student.Branch).order_by('name')
    if request.method == 'GET':  # If the form is submitted
        search_query = request.GET.get('search_box')
        if search_query:
            prof = Professor.objects.filter(dept=request.user.student.Branch, aoi__contains=search_query).order_by('name')
    cf = request.user.student.choice_set.all().order_by('priority')
    prof_filled = []
    for e in cf:
        prof_filled.append(e.professor)
    req = GroupRequest.objects.filter(receiver=request.user.student).count()
    context = {'Professor_list': prof, 'Notification_list':Notification.objects.order_by('-pub_date'),
               'Filled_Choices': prof_filled, 'choices_filled': cf, 'request_count': req}
    return render(request, 'students/index.html', context=context)


'''MENTOR DETAIL VIEW'''


class DetailView(generic.DetailView):
    model = Professor

    def get_template_names(self):
        try:
            usr = self.request.user.student
        except Student.DoesNotExist:
            usr = None
        if usr is not None:
            return 'students/detail.html'
        return 'students/dep_detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Professor.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            req = GroupRequest.objects.filter(receiver=self.request.user.student).count()
        except Student.DoesNotExist:
            req = 0
        try:
            prof = Professor.objects.filter(dept=self.request.user.student.Branch).order_by('name')
            if self.request.method == 'GET':  # If the form is submitted
                search_query = self.request.GET.get('search_box')
                if search_query:
                    prof = Professor.objects.filter(dept=self.request.user.student.Branch, aoi__contains=search_query).order_by(
                        'name')
            cf = self.request.user.student.choice_set.all().order_by('priority')
            prof_filled = []
            for e in cf:
                prof_filled.append(e.professor)
            context['Notification_list'] = Notification.objects.order_by('-pub_date')
            context['Professor_list'] = prof
            context['Filled_Choices'] = prof_filled
            context['choices_filled'] = cf
            context['request_count'] = req
        except Student.DoesNotExist:
            pass
        try:
            user = self.request.user
            context['Students_List'] = Student.objects.filter(Branch=user.department.dep_name)
            context['Professors_List'] = Professor.objects.filter(dept=user.department.dep_name)
            notification_list = Notification.objects.order_by('-pub_date')
            context['Notification_list'] = notification_list
            superuser = User.objects.filter(is_superuser=True)[0]
            context['superuser'] = superuser
        except Department.DoesNotExist:
            pass
        return context


'''ADD PREFERENCE VIEW'''


class AddView(generic.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'students:faculty_index'

    def get_redirect_url(self, *args, **kwargs):
        prof = get_object_or_404(Professor, pk=kwargs['pk'])
        self.request.user.student.add_preference(prof)
        self.request.user.student.save()
        return super().get_redirect_url(*args, **kwargs)


'''REMOVE PREFERENCE VIEW'''


class RemoveView(generic.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        prof = get_object_or_404(Professor, pk=kwargs['pk'])
        self.request.user.student.del_preference(prof)
        self.request.user.student.save()
        return super().get_redirect_url(*args, **kwargs)


'''DEPARTMENT LOGIN VIEW, NOT IN USE'''


class DepLoginView(LoginView):
    authentication_form = DepartmentLoginForm
    redirect_field_name = 'students:dep_home'
    next = 'students:dep_home'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Notification_list'] = Notification.objects.order_by('-pub_date')
        context['next'] = self.next
        return context


'''DEPARTMENT HOME VIEW'''


class DepHomeView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'students/dep_home.html'
    login_url = '/'

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


'''DEPARTMENT LOGIN VIEW, NOT IN USE'''


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


'''ADD MENTOR VIEW, NOT IN USE'''


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


'''ADD MENTOR VIEW, IN USE'''


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
    context = {'form': form, 'Notification_list': Notification.objects.order_by('-pub_date')}
    user = request.user
    context['Students_List'] = Student.objects.filter(Branch=user.department.dep_name)
    context['Professors_List'] = Professor.objects.filter(dept=user.department.dep_name)
    notification_list = Notification.objects.order_by('-pub_date')
    context['Notification_list'] = notification_list
    superuser = User.objects.filter(is_superuser=True)[0]
    context['superuser'] = superuser
    return render(request, 'students/faculty_form.html', context)


'''ADD STUDENT VIEW, NOT IN USE'''


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


'''ADD STUDENT VIEW, IN USE'''


@login_required(login_url='/accounts/login')
def student_add_view(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            stud = form.save(commit=False)
            username = form.cleaned_data.get('registration_no')
            email = form.cleaned_data.get('email')
            dob = form.cleaned_data.get('Date_of_Birth')
            try:
                users = User.objects.create_user(username=username, email=email, password='qwertyuiop')
            except IntegrityError:
                return HttpResponse("Registration Number Already Exists!!!")
            stud.reg_no = users
            dep = User.objects.filter(username=request.user.username)[0]
            stud.Branch = dep.department.dep_name
            stud.DOB = dob
            stud = stud.save()
            return redirect('students:add_student')
    else:
        form = StudentForm()
    context = {'form': form, 'Notification_list': Notification.objects.order_by('-pub_date')}
    user = request.user
    context['Students_List'] = Student.objects.filter(Branch=user.department.dep_name)
    context['Professors_List'] = Professor.objects.filter(dept=user.department.dep_name)
    notification_list = Notification.objects.order_by('-pub_date')
    context['Notification_list'] = notification_list
    superuser = User.objects.filter(is_superuser=True)[0]
    context['superuser'] = superuser
    return render(request, 'students/student_form.html', context=context)


'''SEND REQUEST VIEW'''


class SendRequestView(SuccessMessageMixin, generic.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'students:student_home'
    success_message = "Request Sent Successfully!!"

    def get_redirect_url(self, *args, **kwargs):
        receiver = get_object_or_404(Student, pk=kwargs['pk'])
        GroupRequest.objects.create(sender=self.request.user.student, receiver=receiver)
        messages.success(self.request, "Request sent successfully!!")
        return super().get_redirect_url(*args, **kwargs)

    def get_success_message(self, cleaned_data):
        return self.success_message


'''UPDATE STUDENT VIEW'''


class StudentUpdate(SuccessMessageMixin, generic.UpdateView):
    model = Student
    fields = ['Name', 'FName', 'DOB', 'CPI', 'Category', 'Semester']
    template_name_suffix = '_form'
    success_url = '/accounts/department/home'
    success_message = "Student info was edited successfully!!"

    def get_success_message(self, cleaned_data):
        return self.success_message

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


'''UPDATE FACULTY VIEW'''


class FacultyUpdate(SuccessMessageMixin, generic.UpdateView):
    model = Professor
    fields = ['pid', 'name', 'desg', 'qual', 'aoi', 'group']
    template_name = 'students/faculty_form.html'
    success_url = '/accounts/department/home'
    success_message = "Mentor info was edited successfully!!"

    def get_success_message(self, cleaned_data):
        return self.success_message

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


'''RESETS EVERYTHING, APART FROM USER DIRECTION AND UPLOADED INFORMATION'''


@login_required(login_url='/admin')
def reset_view(request):
    if request.user.is_superuser:
        students = list(Student.objects.filter(leader=False))
        for s in students:
            print(s)
            setattr(s, 'group', None)
            setattr(s, 'mentor', None)
            s.save()
            print(s.group)

        leaders = list(Student.objects.filter(leader=True))
        for l in leaders:
            setattr(l, 'leader', False)
            setattr(l, 'choices_filled', False)
            setattr(l, 'group', None)
            setattr(l, 'mentor', None)
            l.save()

        choices = list(Choice.objects.all())
        for c in choices:
            c.delete()

        grps = list(Group.objects.all())
        for g in grps:
            g.delete()

        req = GroupRequest.objects.all()
        for r in req:
            r.delete()

        notifications = list(Notification.objects.all())
        for n in notifications:
            n.delete()

    else:
        messages.warning(request, "Access Denied, Unauthorized access!")
    return redirect('home')


@login_required(login_url='/admin')
def reset_result(request):
    if request.user.is_superuser:
        students = list(Student.objects.all())
        for s in students:
            setattr(s, 'mentor', None)
            s.save()
        return redirect('home')
    else:
        messages.warning(request, "Access Denied, unauthorized attempt!")
        return redirect('home')
