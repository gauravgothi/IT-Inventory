from django.http import JsonResponse

from assignments.views import admin_required
from miscellaneous.serializers import CategorySubcategorySerializer
from utility.models import CustomError
from .models import CategorySubcategory, Status, Condition
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes

def get_status_and_condition_values(request):
    try:
        status_values = Status.get_status_values() 
        condition_values = Condition.get_condition_values()
        status_list = []
        condition_list = []

        for status in status_values:
            status_list.append(status.status_values)
        for condition in condition_values:
            condition_list.append(condition.condition_values)

        return JsonResponse({'status__list': status_list,'condition_list': condition_list}, status=500)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def get_status_values(request):
    try:
        status_values = Status.get_status_values() 
        status_list = []
        
        for status in status_values:
            status_list.append(status.status_values)
        return JsonResponse({'status_list': status_list},status = 200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def get_condition_values(request):
    try:
        condition_values = Condition.get_condition_values()
        condition_list = []

        for condition in condition_values:
            condition_list.append(condition.condition_values)

        return JsonResponse({'condition_list': condition_list},status = 200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def get_categories(request):
    try:
        category_values = CategorySubcategory.get_categories()
        return JsonResponse({'category_list': category_values},status = 200)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def get_subcategories(request,category):
    try:
        subcategory_values = CategorySubcategory.get_subcategories(category)
        return JsonResponse({'subcategory_list': subcategory_values},status = 200)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def get_categories_subcategories(request):
    try:
        categories_subcategories_list = CategorySubcategory.objects.all()

        if categories_subcategories_list.exists():
            categories_subcategories_data  = list(categories_subcategories_list.values())
            return JsonResponse(categories_subcategories_data,status = 200,safe=False)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@api_view(["POST"])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_category(request):
    try:
        category = request.data.get('category')
        default_subcategory = request.data.get('default_subcategory', 'Not Added')
        # Check if the category exists (case-insensitive)
        if CategorySubcategory.objects.filter(category__iexact=category).exists():
            raise CustomError('Category already exists')
        
        serializer = CategorySubcategorySerializer(data={'category': category, 'subcategory': default_subcategory})
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'status': 'success', 'message': 'Category added successfully.'}, status=201)
    except CustomError as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@api_view(["POST"])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_subcategory(request):
    try:
        category = request.data.get('category')
        subcategory = request.data.get('subcategory')
        
         # Check if the category exists (case-insensitive)
        if not CategorySubcategory.objects.filter(category__iexact=category).exists():
            return CustomError('Category does not exist.')
        
        # Check if the subcategory exists for the given category
        if CategorySubcategory.objects.filter(category__iexact=category, subcategory__iexact=subcategory).exists():
            raise CustomError('Sub-Category already exists')
        
        # Check if "Not Added" subcategory exists for the given category
        not_added_instance = CategorySubcategory.objects.filter(category__iexact=category, subcategory='Not Added').first()
        
        if not_added_instance:
            # Update the "Not Added" subcategory
            not_added_instance.subcategory = subcategory
            not_added_instance.save()
            return JsonResponse({'status': 'success', 'message': 'Sub-Category updated successfully.'}, status=200)
        
        serializer = CategorySubcategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'status': 'success', 'message': 'Sub-Category added successfully.'}, status=200)
    except CustomError as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)