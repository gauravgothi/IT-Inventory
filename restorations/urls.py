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
    path('create_restoration/',views.create_restoration, name='create_restoration'),
    path('restoration_done/<int:restoration_id>/', views.restoration_done, name='restoration_done'),
    path('get_restoration_list/<int:restoration_id>/',views.get_restoration_list, name='get_restoration_list_by_id'),
    path('get_restoration_list/',views.get_restoration_list, name='get_restoration_list_by_filter'),
]