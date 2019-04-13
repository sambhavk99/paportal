from .views import *
from django.urls import path
import uuid

app_name = 'notifications'
urlpatterns = [
    path('', index_view, name='index'),
    path('<uuid:pk>/', DetailView.as_view(), name='detail'),
]
