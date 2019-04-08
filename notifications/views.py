from django.shortcuts import render
from .models import Notification
from django.views import generic
from django.contrib.auth.models import User

def index_view(request):
    user = User.objects.filter(is_superuser=True)[0]
    user.userdirection.create()
    nl = Notification.objects.order_by('-pub_date')
    ctx = {'Notification_list': nl, 'superuser':user}
    return render(request, template_name='notifications/index.html', context=ctx)


class DetailView(generic.DetailView):
    model = Notification
    template_name = 'notifications/detail.html'

    def get_queryset(self):
        return Notification.objects.all()




