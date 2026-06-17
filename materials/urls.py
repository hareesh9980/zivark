from django.urls import path
from . import views

app_name = 'materials'

urlpatterns = [
    path('',                    views.material_list,     name='list'),
    path('add/',                views.material_add,      name='add'),
    path('<int:pk>/edit/',      views.material_edit,     name='edit'),
    path('<int:pk>/toggle/',    views.material_toggle,   name='toggle'),
    path('rules/add/',          views.weight_rule_add,   name='rule_add'),
    path('rules/<int:pk>/edit/',views.weight_rule_edit,  name='rule_edit'),
]