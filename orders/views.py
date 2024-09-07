from datetime import datetime, timedelta, timezone
from functools import wraps
import json
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

indian_time = timezone(timedelta(hours=5, minutes=30))

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            #return redirect('login')
        if not request.user.role=='ADMIN':
            return JsonResponse({'error': 'Admin access required'}, status=403)
            #return HttpResponse('Admin access required', status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@csrf_exempt
@api_view(["POST"])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        data = json.loads(request.body)
        order = Order(
            po_number = data.get('po_number'),
            po_type = data.get('po_type'),
            project_id = data.get('project_id'),
            project_name = data.get('project_name'),
            supplier_id = data.get('supplier_id'),
            supplier_name = data.get('supplier_name'),
            purchase_date=data.get('purchaset_date'),
            
            created_by=request.user.username,
            created_on=datetime.now(tz=indian_time)
        )
        order.save()

        return JsonResponse({'status': 'success', 'message': f'Order {order.po_number} added successfully.'}, status=201)
    except IntegrityError as e:
        if 'unique constraint' in str(e):
            return JsonResponse({'status': 'error', 'message': f'Order number {order.po_number} must be unique.'}, status=400)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing field: {e.args[0]}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

@api_view(["PUT"])
@admin_required
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def update_order(request, order_id):
    try:
        data = json.loads(request.body)
        order = Order.objects.get(id=order_id)

        order.po_type = data.get('po_type'),
        order.project_id = data.get('project_id'),
        order.project_name = data.get('project_name'),
        order.supplier_id = data.get('supplier_id'),
        order.supplier_name = data.get('supplier_name'),
        order.purchase_date=data.get('purchaset_date'),

        order.updated_by = request.user.username
        order.updated_on = datetime.now(tz=indian_time)

        order.save()

        return JsonResponse({'status': 'success', 'message': f'Order {order.po_number} updated successfully.'}, status=200)
    except IntegrityError as e:
        if 'unique constraint' in str(e):
            return JsonResponse({'status': 'error', 'message': f'Order number {order.po_number} must be unique.'}, status=400)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Equipment not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_order_list(request, order_id=None):
    try:
        # Get optional filter parameters from the request
        po_number = request.GET.get('po_number')
        supplier_id = request.GET.get('supplier_id')
        project_id = request.GET.get('project_id')
        
        # Build the query using Q objects for optional filtering
        filters = Q()
        if po_number:
            filters &= Q(po_number=po_number)
        if supplier_id:
            filters &= Q(supplier_id=supplier_id)
        if project_id:
            filters &= Q(project_id=project_id)
        
        if order_id:
            filters &= Q(id=order_id)

        # Query the Equipment model with the constructed filters
        order_list = Order.objects.filter(filters)

        if order_list.exists():
            order_list_data = list(order_list.values())
            return JsonResponse(order_list_data, status=status.HTTP_200_OK, safe=False)
        else:
            return JsonResponse({'error': 'No order found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
