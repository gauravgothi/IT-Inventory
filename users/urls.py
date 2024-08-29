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
from django.contrib import admin
from django.urls import include, path
from . import views


urlpatterns = [
    path('login/',views.LoginView.as_view(), name='login'),
    path('get_user/<str:username>',views.get_user, name='get_user'),
    path('add_user/',views.add_user, name='add_user'),
    path('update_user/<int:user_id>/', views.update_user, name='update_user'),
    path('deactivate_user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    
    path('home/', views.home, name='home'),  # Add this line if you have a home view
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Add this line if you have an admin dashboard view
]