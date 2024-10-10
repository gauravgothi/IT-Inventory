from django.urls import path
from . import views

urlpatterns = [
    path('status-condition/', views.get_status_and_condition_values, name='status-condition'),
    path('status/', views.get_status_values, name='status'),
    path('condition/', views.get_condition_values, name='condition'),
    path('category/',views.get_categories,name='category'),
    path('subcategory/<str:category>/',views.get_subcategories,name='subcategory'),
    path('category_subcategory_all/',views.get_categories_subcategories,name='category_subcategory_all'),
    path('add-category/', views.create_category, name='add-category'),
    path('add-subcategory/', views.create_subcategory, name='add-subcategory'),
]