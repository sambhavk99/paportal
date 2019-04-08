from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from .forms import MessageForm
from .models import Message
from notifications.models import Notification
from students.models import Student
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages


'''class CreateMessage(SuccessMessageMixin, generic.FormView):
    template_name = 'django_messages/create.html'
    form_class = MessageForm
    success_url = '/messages'
    success_message = "Message sent successfully"
    ib = Message.objects.all().filter(receiver=request.user.student).order_by('-created_at')
    extra_context = {}

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        receiver = self.request.user.groups.all()[0]
        print(receiver)
        msg = form.save(commit=False)
        msg.sender = self.request.user.student
        msg.receiver = receiver
        msg = msg.save()
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message
'''


@login_required(login_url='/accounts/login')
def create_message(request):
    try:
        msgs = Message.objects.all().filter(receiver=request.user.groups.all()[0]).order_by('created_at')
    except IndexError:
        msgs = None
        pass
    form = MessageForm()
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user.student
            msg.receiver = request.user.student.group
            msg = msg.save()
            messages.success(request, "Message sent successfully")
            return redirect('django_messages:chats')

    ctx = {'form': form, 'Messages': msgs}

    return render(request, 'django_messages/chat.html', ctx)


def home(request):
    group = request.user.groups.all()[0]
    members = group.user_set.all()

    ctx = {'members': members}
    return render(request, 'django_messages/home.html', context=ctx)


def inbox(request):
    ib = Message.objects.all().filter(receiver=request.user.student).order_by('-created_at')
    snt = Message.objects.all().filter(sender=request.user.student).order_by('-created_at')

    context = {
        'inbox': ib,
        'sent': snt,
        'Notification_list': Notification.objects.order_by('-pub_date')

    }

    return render(request, 'django_messages/inbox.html', context=context)


class DetailView(generic.DetailView):
    model = Message
    print("Hi")
    template_name = 'django_messages/detail.html'
    setattr(model, 'seen', True)

    def get_queryset(self):
        msg = Message.objects.filter(pk=self.kwargs['pk'])[0]
        if self.request.user.student == msg.receiver:
            #setattr(msg, 'seen', True)
            msg.save()
        return Message.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Notification_list'] = Notification.objects.order_by('-pub_date')
        context['inbox'] = Message.objects.all().filter(receiver=self.request.user.student),
        context['sent'] = Message.objects.all().filter(sender=self.request.user.student),
        return context




