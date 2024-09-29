from datetime import date, datetime, timedelta, timezone
from functools import wraps
from django.db.models import Count, Sum
import json
from django.db.models import TextField
from django.db import IntegrityError,transaction
from django.forms import CharField, model_to_dict
from django.http import JsonResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from assignments.models import Assignment
from django.contrib.postgres.search import SearchVector
from assignments.serializers import AssignmentSerializer
from equipments.models import Equipment
from equipments.serializers import EquipmentSerializer
from miscellaneous.models import Condition, Status
from orders.models import Order
from users.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from utility.models import CustomError

indian_time = timezone(timedelta(hours=5, minutes=30))

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if not request.user.role=='ADMIN':
            return JsonResponse({'error': 'Admin access required'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def json_validation(data):
    status=data.get('status')
    condition = data.get('condition')
    serial_number = data.get('serial_number')

    valid_status = [status.status_values for status in Status.objects.all()]
    valid_conditions = [condition.condition_values for condition in Condition.objects.all()]

    if status not in valid_status:
        raise CustomError("Item Status is not valid")
    elif condition not in valid_conditions:
        raise CustomError("Item Condition is not valid")
    elif status == 'RETURN TO STORE':
        raise CustomError("Add Item and Edit item not allow status 'return to store'.")
    elif serial_number == '':
        raise CustomError('Serial Number cannot be blank.')
    
    


@csrf_exempt
@api_view(["POST"])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_equipment(request):
    try:
        data = json.loads(request.body)
        json_validation(data)

        serial_no = data.get('serial_number')
        serial_no = serial_no.strip() if serial_no else None

        equipment = Equipment(
            category=data.get('category'),
            sub_category=data.get('sub_category'),
            make=data.get('make'),
            model=data.get('model'),
            serial_number = serial_no,
            order=data.get('order_id'),
            receipt_date=data.get('receipt_date'),
            price = data.get('price'),
            warranty_expiration=data.get('warranty_expiration'),
            status=data.get('status'),
            condition = data.get('condition'),
            assignment_id=data.get('assignment_id'),
            notes=data.get('notes'),
            
            created_by=request.user.username,
            created_on=datetime.now(tz=indian_time)
        )
        equipment.save()

        return JsonResponse({'status': 'success', 'message': f'Equipment {equipment.serial_number} added successfully.'}, status=201)
    except CustomError as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=400)
    except IntegrityError as e:
        if 'unique constraint' in str(e):
            return JsonResponse({'status': 'error', 'message': f'Equipment Serial number {equipment.serial_number} must be unique.'}, status=400)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing field: {e.args[0]}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@csrf_exempt
@api_view(["POST"])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_equipment_list(request):
    try:
        data_list = json.loads(request.body)  # Expecting a list of equipment data
        if not isinstance(data_list, list):
            return JsonResponse({'status': 'error', 'message': 'Invalid data format, expected a list of equipment.'}, status=400)
        elif len(data_list) == 0:
            raise CustomError('expecting atleast one item.')

        with transaction.atomic():  # Start an atomic transaction block
            for data in data_list:
                json_validation(data)

                serial_no = data.get('serial_number')
                serial_no = serial_no.strip() if serial_no else None

                Equipment.objects.create(
                    category=data.get('category'),
                    sub_category=data.get('sub_category'),
                    make=data.get('make'),
                    model=data.get('model'),
                    serial_number=serial_no,
                    order=Order.objects.get(id=data.get('order_id')),
                    receipt_date=data.get('receipt_date'),
                    price = data.get('price'),
                    warranty_expiration=data.get('warranty_expiration'),
                    status=data.get('status'),
                    condition = data.get('condition'),
                    assignment_id=data.get('assignment_id'),
                    notes=data.get('notes'),
                    created_by=request.user.username,
                    created_on=datetime.now(tz=indian_time)
                )

        return JsonResponse({'status': 'success', 'message': 'All equipment added successfully.'}, status=201)

    except CustomError as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=400)
    except IntegrityError as e:
        # This catches any IntegrityError such as a unique constraint violation during the transaction
        return JsonResponse({'status': 'error', 'message': 'Transaction failed. ' + str(e)}, status=400)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing field: {e.args[0]}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@api_view(["PUT"])
@admin_required
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def update_equipment(request, equipment_id):
    try:
        data = json.loads(request.body)
        json_validation(data)
        equipment = Equipment.objects.get(id=equipment_id)

        equipment.category = data.get('category', equipment.category)
        equipment.sub_category = data.get('sub_category', equipment.sub_category)
        equipment.make = data.get('make', equipment.make)
        equipment.model = data.get('model', equipment.model)
        equipment.serial_number = data.get('serial_number', equipment.serial_number)

        equipment.order = Order.objects.get(id= data.get('order_id'))

        equipment.receipt_date = data.get('receipt_date',equipment.receipt_date)
        equipment.price = data.get('price',equipment.price)
        equipment.warranty_expiration = data.get('warranty_expiration',equipment.warranty_expiration)
        equipment.status = data.get('status',equipment.status)
        equipment.condition = data.get('condition',equipment.condition)
        equipment.assignment_id = data.get('assignment_id',equipment.assignment_id)
        equipment.notes = data.get('notes',equipment.notes)

        equipment.updated_by = request.user.username
        equipment.updated_on = datetime.now(tz=indian_time)

        equipment.save()

        return JsonResponse({'status': 'success', 'message': f'Equipment {equipment.serial_number} updated successfully.'}, status=200)
    except CustomError as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=400)
    except IntegrityError as e:
        if 'unique constraint' in str(e):
            return JsonResponse({'status': 'error', 'message': f'Equipment Serial number {equipment.serial_number} must be unique.'}, status=400)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    except Equipment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Equipment not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@api_view(["DELETE"])
@admin_required
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def delete_equipment(request, equipment_id):
    try:
        equipment = Equipment.objects.get(id=equipment_id)
        equipment.delete()

        return JsonResponse({'status': 'success', 'message': f'Equipment {equipment.serial_number} deleted successfully.'}, status=200)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': f'Equipment {equipment.serial_number} not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_equipment_list(request, equipment_id=None):
    try:
        # Get optional filter parameters from the request
        serial_number = request.GET.get('serial_number')
        order = request.GET.get('order')
        purchase_date = request.GET.get('purchase_date')
        
        # Build the query using Q objects for optional filtering
        filters = Q()
        if serial_number:
            filters &= Q(serial_number=serial_number)
        if order:
            filters &= Q(order=order)
        if purchase_date:
            filters &= Q(purchase_date=purchase_date)
        
        if equipment_id:
            filters &= Q(id=equipment_id)

        # Query the Equipment model with the constructed filters
        equipment_list = Equipment.objects.filter(filters)

        if equipment_list.exists():
            equipment_data = list(equipment_list.values())
            return JsonResponse(equipment_data, status=status.HTTP_200_OK, safe=False)
        else:
            return JsonResponse({'status': 'error','message': 'No equipment found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)
    except Equipment.DoesNotExist:
        return JsonResponse({'status': 'error','message': 'Equipment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'status': 'error','message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_equipment_list_with_serializer(request, equipment_id=None):
    try:
        # Get optional filter parameters from the request
        serial_number = request.GET.get('serial_number')
        order = request.GET.get('order')
        purchase_date = request.GET.get('purchase_date')
        
        # Build the query using Q objects for optional filtering
        filters = Q()
        if serial_number:
            filters &= Q(serial_number=serial_number)
        if order:
            filters &= Q(order=order)
        if purchase_date:
            filters &= Q(purchase_date=purchase_date)
        
        if equipment_id:
            filters &= Q(id=equipment_id)

        # Query the Equipment model with the constructed filters
        equipment_list = Equipment.objects.filter(filters).order_by('id')
        serializer = EquipmentSerializer(equipment_list,many = True)
        if equipment_list.exists():
            equipment_data = serializer.data
            for data in equipment_data:
                data['assignment'] = model_to_dict(Assignment.objects.get(id = data['assignment_id'])) if data['assignment_id'] != None else None
            return JsonResponse(equipment_data, status=status.HTTP_200_OK, safe=False)
        else:
            return JsonResponse({'status': 'error','message': 'No equipment found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)
    except Equipment.DoesNotExist:
        return JsonResponse({'status': 'error','message': 'Equipment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'status': 'error','message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_equipment_list_with_pagination(request, equipment_id=None):
    try:
        # Get the search query
        search_query = request.GET.get('search')

        # Get optional filter parameters from the request
        serial_number = request.GET.get('serial_number')
        order = request.GET.get('order')
        purchase_date = request.GET.get('purchase_date')

        # Get pagination parameters
        page_number = int(request.GET.get('page_number', 1))  # Default to page 1
        page_size = int(request.GET.get('page_size', 50))  # Default page size is 50

        # Build the query using Q objects for optional filtering
        filters = Q()
        if serial_number:
            filters &= Q(serial_number=serial_number)
        if order:
            filters &= Q(order=order)
        if purchase_date:
            filters &= Q(purchase_date=purchase_date)

        if equipment_id:
            filters &= Q(id=equipment_id)

        # Dynamically generate SearchVector based on all CharField or TextField fields in the Equipment model
        search_fields = [
            field.name for field in Equipment._meta.get_fields() 
            if isinstance(field, (CharField, TextField))
        ]
        search_vector = SearchVector(*search_fields)

        print("Search fields:", search_fields)
        print("Search vector:", search_vector)

        # Apply full-text search if search_query is provided
        if search_query:
            equipment_list = Equipment.objects.annotate(search=search_vector).filter(search=search_query)
        else:
            equipment_list = Equipment.objects.filter(filters)

        # Get the total count before pagination
        total_count = equipment_list.count()

        # Apply pagination manually
        start = (page_number - 1) * page_size
        end = start + page_size
        paginated_list = equipment_list[start:end]

        # Serialize the paginated results
        serializer = EquipmentSerializer(paginated_list, many=True)
        
        # Add assignment data if it exists
        equipment_data = serializer.data
        for data in equipment_data:
            data['assignment'] = model_to_dict(Assignment.objects.get(id=data['assignment_id'])) if data.get('assignment_id') else None
        
        # Construct the response with pagination metadata
        response_data = {
            'results': equipment_data,
            'total_count': total_count,
            'page_number': page_number,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,  # Total pages calculation
        }

        return JsonResponse(response_data, status=status.HTTP_200_OK)

    except Equipment.DoesNotExist:
        return JsonResponse({'status' : 'error','message': 'Equipment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'status' : 'error','message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])  
def get_equipment_overview(request):
    try:
        # Total number of equipment
        total_equipment_count = Equipment.objects.count()
        
        # Count by category and subcategory
        category_summary = Equipment.objects.values('category', 'sub_category').annotate(count=Count('id'))
        
        # Equipment status summary
        status_summary = Equipment.objects.values('status','condition').annotate(count=Count('id'))
        
        overview = {
            'total_equipment_count': total_equipment_count,
            'category_summary': list(category_summary),
            'status_summary': list(status_summary)
        }
        return JsonResponse({'data': overview}, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])  
def get_equipment_condition_summary(request):
    try:
        # Equipment condition distribution
        condition_summary = Equipment.objects.values('condition').annotate(count=Count('id'))
        
        summary = {
            'condition_summary': list(condition_summary),
        }
        return JsonResponse({'data': summary}, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])  
def get_purchase_and_warranty_summary(request):
    try:
        # Equipment nearing warranty expiration (within 3 months)
        upcoming_expiration_date = date.today() + timedelta(days=90)
        upcoming_warranty_expirations = Equipment.objects.filter(warranty_expiration__date__lte=upcoming_expiration_date, warranty_expiration__date__gte=date.today())
    
        # Warranty status
        warranty_status_summary = {
            'in_warranty': Equipment.objects.filter(warranty_expiration__date__gte=date.today()).count(),
            'expired_warranty': Equipment.objects.filter(warranty_expiration__date__lt=date.today()).count(),
            'no_warranty': Equipment.objects.filter(warranty_expiration__isnull=True).count()
        }
    
        # Total purchase value
        total_purchase_value = Equipment.objects.aggregate(total_value=Sum('price'))['total_value']
    
        summary = {
            'upcoming_warranty_expirations': list(upcoming_warranty_expirations.values('id', 'category', 'model', 'serial_number', 'warranty_expiration')),
            'warranty_status_summary': warranty_status_summary,
            # 'total_purchase_value': total_purchase_value
        }
        return JsonResponse({'data': summary}, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


