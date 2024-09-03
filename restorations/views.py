from datetime import datetime
from functools import wraps
import json
from django.db import IntegrityError,transaction
from django.http import JsonResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from assignments.models import Assignment
from equipments.models import Equipment
from restorations.models import Restoration
from users.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if not request.user.role=='ADMIN':
            return JsonResponse({'error': 'Admin access required'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@csrf_exempt
@api_view(["POST"])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_restoration(request):
    try:
        data = json.loads(request.body)
        restoration = Restoration.objects.create(
            equipment = data.get('equipment_id'),
            restoration_date = data.get('restoration_date'),
            performed_by = data.get('performed_by'),
            description = data.get('description'),
            estimated_cost = data.get('estimated_cost'),
            estimated_delivery_date = data.get('estimated_delivery_date'),
            delivery_date = data.get('delivery_date'),
            actual_cost = data.get('actual_cost'),
            invoice_number = data.get('invoice_number'),
            invoice_date = data.get('invoice_number'),

            created_by=request.user.username,
            created_on=datetime.now()
        )
        restoration_equipment = Equipment.objects.get(id=restoration.equipment)
        if restoration_equipment.status == "AVAILABLE":
            with transaction.atomic():
                restoration_equipment.status = "IN_RESTORATION"
                restoration_equipment.save()
                restoration.save()
        else:
            return JsonResponse({'status': 'error', 'message': 'Equipment Serial number {restoration_equipment.serial_number} must be in available status.'}, status=400)
        
        return JsonResponse({'status': 'success', 'message': 'Equipment {restoration_equipment.serial_number} assigned to {restoration.performed_by} successfully for restoration.'}, status=201)
    except IntegrityError as e:
        if 'unique constraint' in str(e):
            return JsonResponse({'status': 'error', 'message': 'Equipment Serial number {issueing_equipment.serial_number} must be unique.'}, status=400)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing field: {e.args[0]}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

@csrf_exempt
@api_view(["PUT"])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def restoration_done(request,restoration_id):
    try:
        data = json.loads(request.body)
        restoration = Restoration.objects.get(id=restoration_id)
        restoration.delivery_date = data.get('delivery_date'),
        restoration.actual_cost = data.get('actual_cost'),
        restoration.invoice_number = data.get('invoice_number'),
        restoration.invoice_date = data.get('invoice_date'),
    
        restoration.updated_by=request.user.username,
        restoration.updated_on=datetime.now()

        restored_equipment = Equipment.objects.get(id=restoration.equipment)
        if restored_equipment.status == "IN_RESTORATION":
            with transaction.atomic():
                restored_equipment.status = "AVAILABLE"
                restored_equipment.save()
                restoration.save()
        else:
            return JsonResponse({'status': 'error', 'message': 'Equipment Serial number {issueing_equipment.serial_number} must be in issued status.'}, status=400)
        
        return JsonResponse({'status': 'success', 'message': 'Equipment {returning_equipment.serial_number} returned from {assignment.assigned_type} {assignment.assign_to} to store successfully.'}, status=201)
    except IntegrityError as e:
        if 'unique constraint' in str(e):
            return JsonResponse({'status': 'error', 'message': 'Equipment Serial number {issueing_equipment.serial_number} must be unique.'}, status=400)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing field: {e.args[0]}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
