from datetime import datetime
from functools import wraps
import json
from django.db import IntegrityError,transaction
from django.http import JsonResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from assignments.models import Assignment
from equipments.models import Equipment
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
def issue_equipment(request):
    try:
        data = json.loads(request.body)
        assignment = Assignment.objects.create(
            equipment = data.get('equipment_id'),
            assigned_type = data.get('assigned_type'),
            assign_to = data.get('assignee_id'),
            assigned_date = data.get('assigned_date'),
            # return_date = data.get('return_date'),
            assigned_condition = data.get('assigned_condition'),
            # returned_condition = data.get('returned_condition'),
            notes = data.get('notes'),

            created_by=request.user.username,
            created_on=datetime.now()
        )
        issueing_equipment = Equipment.objects.get(id=assignment.equipment)
        if issueing_equipment.status == "AVAILABLE":
            with transaction.atomic():
                issueing_equipment.status = "ISSUED"
                issueing_equipment.save()
                assignment.save()
        else:
            return JsonResponse({'status': 'error', 'message': 'Equipment Serial number {issueing_equipment.serial_number} must be in available status.'}, status=400)
        
        return JsonResponse({'status': 'success', 'message': 'Equipment {issueing_equipment.serial_number} assigned to {assignment.assigned_type} {assignment.assign_to} successfully.'}, status=201)
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
def receive_equipment(request,assignment_id):
    try:
        data = json.loads(request.body)
        assignment = Assignment.objects.get(id=assignment_id)
        assignment.return_date = data.get('return_date'),
        assignment.assigned_condition = data.get('assigned_condition'),
        assignment.notes = data.get('notes'),

        assignment.updated_by=request.user.username,
        assignment.updated_on=datetime.now()

        returning_equipment = Equipment.objects.get(id=assignment.equipment)
        if returning_equipment.status == "ISSUED":
            with transaction.atomic():
                returning_equipment.status = "AVAILABLE"
                returning_equipment.save()
                assignment.save()
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
