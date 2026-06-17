from django.urls import path
from . import views

app_name = 'rfq'

urlpatterns = [
    path('',              views.rfq_list,     name='list'),
    path('new/',          views.rfq_new,      name='new'),
    path('<int:pk>/',     views.rfq_detail,   name='detail'),
    path('<int:pk>/generate/', views.rfq_generate, name='generate'),
    path('<int:pk>/status/',   views.rfq_status,   name='status'),
]