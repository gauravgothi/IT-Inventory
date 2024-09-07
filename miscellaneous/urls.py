from django.urls import path
from . import views

urlpatterns = [
    path('status-condition/', views.get_status_and_condition_values, name='status-condition'),
    path('status/', views.get_status_values, name='status'),
    path('condition/', views.get_condition_values, name='condition'),
]