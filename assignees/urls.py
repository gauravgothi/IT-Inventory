from django.urls import path
from . import views

urlpatterns = [
    path('<str:target_type>/<int:target_code>/', views.get_assignee_data, name='get_assignee_data'),
]
