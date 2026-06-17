from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('',           views.client_list,   name='list'),
    path('new/',       views.client_new,    name='new'),
    path('<int:pk>/',  views.client_detail, name='detail'),
]