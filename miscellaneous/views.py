from django.http import JsonResponse
from .models import CategorySubcategory, Status, Condition

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