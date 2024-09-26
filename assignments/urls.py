"""
URL configuration for itinventory project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views


urlpatterns = [
    path('issue_equipment/',views.issue_equipment, name='issue_equipment'),
    path('receive_equipment/<int:assignment_id>/', views.receive_equipment, name='receive_equipment'),
    path('get_assignment_list/<int:assignment_id>/',views.get_assignment_list,name='get_assignment_list_by_id'),
    path('get_assignment_list/',views.get_assignment_list,name='get_assignment_list_by_filter'),
    path('get_assignment_list_with_serializer/<int:assignment_id>/',views.get_assignment_list_with_serializer,name='get_assignment_list_with_serializer_by_id'),
    path('get_assignment_list_with_serializer/',views.get_assignment_list_with_serializer,name='get_assignment_list_with_serializer_by_filter'),
    path('get_issue_slip/<int:assignment_id>/',views.get_issue_slip,name='get_issue_slip_by_id'),
    path('get_return_slip/<int:assignment_id>/',views.get_return_slip,name='get_return_slip_by_id'),
    path('get_assignment_history/<int:equipment_id>/',views.get_assignment_history,name='get_assignment_history_by_id'),
    path('get_assignment_history/',views.get_assignment_history,name='get_assignment_history_by_filter'),
    path('retirement_report/',views.get_employee_retirement_info,name='get_employee_retirement_info'),
]