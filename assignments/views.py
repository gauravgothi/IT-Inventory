from datetime import datetime, timedelta, timezone
from functools import wraps
from rest_framework import status
import json
from django.db import IntegrityError,transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from assignees.models import Assignee
from assignments.models import Assignment
from assignments.serializers import AssignmentSerializer
from equipments.models import Equipment
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from utility.views import upload_document2

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if not request.user.role=='ADMIN':
            return JsonResponse({'error': 'Admin access required'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

indian_time = timezone(timedelta(hours=5, minutes=30))

@csrf_exempt
@api_view(["POST"])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def issue_equipment(request):
    try:
        # Attempt to get the file from form data; it will be None if not provided
        file = request.FILES.get('file', None)
        #data = json.loads(request.body)
        assignment = Assignment(
            equipment = Equipment.objects.get(id = request.POST.get('equipment_id')),
            assigned_type = request.POST.get('assigned_type'),
            assigned_to = request.POST.get('assignee_id'),
            assigned_date = request.POST.get('assigned_date'),
            assigned_condition = request.POST.get('assigned_condition'),
            # returned_condition = data.get('returned_condition'),
            notes = request.POST.get('notes'),

            created_by=request.user.username,
            created_on=datetime.now(tz=indian_time)
        )
        issueing_equipment = Equipment.objects.get(id=assignment.equipment.id)
        if issueing_equipment.status == "AVAILABLE":
            with transaction.atomic():
                if file:
                    assignment.letter_for_issue = upload_document2(file = file, asignee_type = assignment.assigned_type, asignee_id = assignment.assigned_to)
                assignment.save()
                issueing_equipment.status = "ISSUED"
                issueing_equipment.assignment_id = assignment.id
                #issueing_equipment.condition = assignment.assigned_condition
                issueing_equipment.save()
        else:
            return JsonResponse({'status': 'error', 'message': f'Equipment Serial number {issueing_equipment.serial_number} must be in available status.'}, status=400)
        
        return JsonResponse({'status': 'success', 'message': f'Equipment {issueing_equipment.serial_number} assigned to {assignment.assigned_type} user {assignment.assigned_to} successfully.'}, status=201)
    except IntegrityError as e:
        if 'unique constraint' in str(e):
            return JsonResponse({'status': 'error', 'message': f'Equipment Serial number {issueing_equipment.serial_number} must be unique.'}, status=400)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing field: {e.args[0]}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    except BaseException as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@csrf_exempt
@api_view(["PUT"])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def receive_equipment(request,assignment_id):
    try:
        # Attempt to get the file from form data; it will be None if not provided
        file = request.FILES.get('file', None)
        #data = json.loads(request.body)
        assignment = Assignment.objects.get(id=assignment_id)
        assignment.return_date = request.POST.get('return_date')
        assignment.assigned_condition = request.POST.get('assigned_condition')
        assignment.notes = request.POST.get('notes')
        assignment.updated_by=request.user.username
        assignment.updated_on=datetime.now(tz=indian_time)

        returning_equipment = Equipment.objects.get(id=assignment.equipment.id)
        if returning_equipment.status == "ISSUED":
            with transaction.atomic():
                if file:
                    assignment.letter_for_return = upload_document2(file = file, user_type = assignment.assigned_type, user_id = assignment.assigned_to)
                assignment.save()
                returning_equipment.status = "AVAILABLE"
                returning_equipment.assignment_id = None
                returning_equipment.condition = assignment.returned_condition # return condtion assigned to item condition
                returning_equipment.save()
        else:
            return JsonResponse({'status': 'error', 'message': f'Equipment Serial number {returning_equipment.serial_number} must be in issued status.'}, status=400)
        
        return JsonResponse({'status': 'success', 'message': f'Equipment {returning_equipment.serial_number} returned from {assignment.assigned_type} {assignment.assigned_to} to store successfully.'}, status=200)
    except IntegrityError as e:
        if 'unique constraint' in str(e):
            return JsonResponse({'status': 'error', 'message': f'Equipment Serial number {returning_equipment.serial_number} must be unique.'}, status=400)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing field: {e.args[0]}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    except BaseException as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_assignment_list(request, assignment_id=None):
    try:
        # Get optional filter parameters from the request
        # if equipment_serial_number:
        #     equipment = Equipment.objects.get(serial_number=equipment_serial_number)
        #     return JsonResponse(equipment, status=status.HTTP_200_OK, safe=False)
        assigned_to = request.GET.get('assigned_to')
        assigned_type = request.GET.get('assigned_type')
        assigned_date = request.GET.get('assigned_date')
        
        # Build the query using Q objects for optional filtering
        filters = Q()
        if assigned_to:
            filters &= Q(assigned_to=assigned_to)
        if assigned_type:
            filters &= Q(assigned_type=assigned_type)
        if assigned_date:
            filters &= Q(assigned_date=assigned_date)
        
        if assignment_id:
            filters &= Q(id=assignment_id)

        # Query the Equipment model with the constructed filters
        assignment_list = Assignment.objects.filter(filters)

        if assignment_list.exists():
            assignment_data = list(assignment_list.values())
            return JsonResponse(assignment_data, status=status.HTTP_200_OK, safe=False)
        else:
            return JsonResponse({'error': 'No assignment found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)
    except Equipment.DoesNotExist:
        return JsonResponse({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_assignment_list_with_serializer(request, assignment_id=None):
    try:
        # Get optional filter parameters from the request
        # if equipment_serial_number:
        #     equipment = Equipment.objects.get(serial_number=equipment_serial_number)
        #     return JsonResponse(equipment, status=status.HTTP_200_OK, safe=False)
        assigned_to = request.GET.get('assigned_to')
        assigned_type = request.GET.get('assigned_type')
        assigned_date = request.GET.get('assigned_date')
        
        # Build the query using Q objects for optional filtering
        filters = Q()
        if assigned_to:
            filters &= Q(assigned_to=assigned_to)
        if assigned_type:
            filters &= Q(assigned_type=assigned_type)
        if assigned_date:
            filters &= Q(assigned_date=assigned_date)
        
        if assignment_id:
            filters &= Q(id=assignment_id)

        # Query the Equipment model with the constructed filters
        assignment_list = Assignment.objects.filter(filters)
        serializer = AssignmentSerializer(assignment_list, many=True)
        if assignment_list.exists():
            assignment_data = serializer.data
            return JsonResponse(assignment_data, status=status.HTTP_200_OK, safe=False)
        else:
            return JsonResponse({'error': 'No assignment found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)
    except Equipment.DoesNotExist:
        return JsonResponse({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
