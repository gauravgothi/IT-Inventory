from django.urls import path
from . import views

urlpatterns = [
    path('upload/document/', views.upload_document, name='upload_document'),
    path('upload/spreadsheet/', views.upload_spreadsheet, name='upload_spreadsheet'),
]
