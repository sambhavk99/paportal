from .views import *
from django.urls import path
import uuid

app_name = 'django_messages'
urlpatterns = [
    path('', home, name='index'),
    #path('<int:pk>/', CreateMessage.as_view(), name='compose'),
    path('inbox/', inbox, name='inbox'),
    path('<uuid:pk>/', DetailView.as_view(), name='detail'),
    path('chats', create_message, name='chats')

    ]
