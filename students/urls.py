from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import *
from django.urls import path, reverse_lazy
from django.conf.urls import url
from django.views.generic import TemplateView

app_name = 'students'
urlpatterns = [
    path('profile/', views.index, name='student_home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(template_name='students/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='students/base.html'), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='students/password_change.html',
                                                                   success_url=reverse_lazy('students:password_change_done'),),
         name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='students/home.html', ),
         name='password_change_done'),
    url(r'password_reset/$', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html',
                                                                  email_template_name='registration/password_reset_email.html',
                                                                  subject_template_name='registration/password_reset_subject.txt',
                                                                  success_url='/accounts/password_reset_done/',
                                                                  from_email='s_9ar@rediffmail.com'), name='password_reset'),
    url(r'password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done'),
    url(r'password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html',
                                                    success_url='/accounts/password_reset_complete/'),
        name='password_reset_confirm'),
    url(r'password_reset_complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'),
    path('create_group/', views.group_view, name='group_creation'),
    path('confirm/', views.confirm_choice, name='confirm_choice'),
    path('send/<int:pk>/', SendRequestView.as_view(url=reverse_lazy('students:student_home')), name='send_request'),
    path('', home, name='index'),
    path('received/', received, name='received'),
    path('sent/', sent, name='sent'),
    path('accept/<uuid:pk>/', AcceptView.as_view(url=reverse_lazy('students:student_home')), name='accepted'),
    path('reject/<uuid:pk>/', RejectView.as_view(url=reverse_lazy('students:received')), name='reject'),
    path('cancel/<uuid:pk>/', CancelView.as_view(url=reverse_lazy('students:sent')), name='cancel'),
    path('mentor', views.index_view, name='faculty_index'),
    path('<int:pk>/', views.DetailView.as_view(), name='faculty_detail'),
    path('add/<int:pk>/', views.AddView.as_view(url=reverse_lazy('students:faculty_index')), name='add'),
    path('remove/<int:pk>/', RemoveView.as_view(url=reverse_lazy('students:faculty_index')), name='remove'),
    path('department/login/', views.dep_login, name='dep_login'),
    path('department/faculty/', views.faculty_add_view, name='add_mentor'),
    path('department/student/', views.student_add_view, name='add_student'),
    path('department/student_update/<int:pk>', StudentUpdate.as_view(), name='edit_student'),
    path('department/home/', DepHomeView.as_view(), name='dep_home'),
    path('department/faculty_update/<int:pk>', FacultyUpdate.as_view(), name='edit_mentor'),


]



