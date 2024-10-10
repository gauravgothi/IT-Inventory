from datetime import datetime, timedelta, timezone
from functools import wraps
import json
from django.shortcuts import render
from django.core.serializers import serialize
from django.db.models import Count
from rest_framework import status
from django.db import IntegrityError,transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from assignees.models import Employee, Location
from assignments.models import Assignment
from assignments.serializers import AssignmentSerializer
from equipments.models import Equipment
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from miscellaneous.models import Condition
from users.models import User
from utility.models import CustomError, IssueSlip
from utility.services import fetch_employee_retirement_info
from utility.views import upload_document2

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status' : 'error','message': 'Authentication required'}, status=401)
        if not request.user.role=='ADMIN':
            return JsonResponse({'status' : 'error','message': 'Admin access required'}, status=403)
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
        #json validation
        assigned_condition = request.POST.get('assigned_condition')
        validate_condition(assigned_condition)

        assignment = Assignment(
            equipment = Equipment.objects.get(id = request.POST.get('equipment_id')),
            assigned_type = request.POST.get('assigned_type','').lower(),
            assigned_to = request.POST.get('assignee_id'),
            assigned_to_details = request.POST.get('assigned_to_details'),
            assigned_date = request.POST.get('assigned_date'),
            assigned_condition = request.POST.get('assigned_condition'),
            returned_condition = None,
            notes = request.POST.get('notes'),

            issue_person_name = request.POST.get('issue_person_name'),
            issue_person_code = request.POST.get('issue_person_code'),

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
                issueing_equipment.condition = assignment.assigned_condition
                issueing_equipment.save()
        else:
            return JsonResponse({'status': 'error', 'message': f'Equipment Serial number {issueing_equipment.serial_number} must be in available status.'}, status=400)
        
        return JsonResponse({'status': 'success', 'assignment_id':f'{issueing_equipment.assignment_id}' , 'message': f'Equipment {issueing_equipment.serial_number} assigned to {assignment.assigned_type} user {assignment.assigned_to} successfully.'}, status=201)
    except CustomError as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=400)
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
        #json validation
        returned_condition = request.POST.get('returned_condition')
        validate_condition(returned_condition)

        assignment = Assignment.objects.get(id=assignment_id)
        assignment.return_date = request.POST.get('return_date')
        assignment.returned_condition = request.POST.get('returned_condition')
        assignment.notes = request.POST.get('notes')

        assignment.return_person_name = request.POST.get('return_person_name')
        assignment.return_person_code = request.POST.get('return_person_code')

        assignment.updated_by=request.user.username
        assignment.updated_on=datetime.now(tz=indian_time)

        returning_equipment = Equipment.objects.get(id=assignment.equipment.id)
        if returning_equipment.status == "ISSUED":
            with transaction.atomic():
                if file:
                    assignment.letter_for_return = upload_document2(file = file, asignee_type = assignment.assigned_type, asignee_id = assignment.assigned_to)
                assignment.save()
                returning_equipment.status = "AVAILABLE"
                returning_equipment.assignment_id = None
                returning_equipment.condition = assignment.returned_condition # return condtion assigned to item condition
                returning_equipment.save()
        else:
            return JsonResponse({'status': 'error', 'message': f'Equipment Serial number {returning_equipment.serial_number} must be in issued status.'}, status=400)
        
        return JsonResponse({'status': 'success','message': f'Equipment {returning_equipment.serial_number} returned from {assignment.assigned_type} {assignment.assigned_to} to store successfully.'}, status=200)
    except CustomError as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=400)
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
            return JsonResponse({'status' : 'error', 'message' : 'No assignment found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)
    except Equipment.DoesNotExist:
        return JsonResponse({'status' : 'error', 'message' : 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

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
            return JsonResponse({'status' : 'error', 'message' : 'No assignment found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)
    except Equipment.DoesNotExist:
        return JsonResponse({'status' : 'error', 'message' : 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

def validate_condition(condition):
    valid_conditions = [condition.condition_values for condition in Condition.objects.all()]

    if condition not in valid_conditions:
        raise CustomError("Assignment Condition is not valid")
    

@api_view(['GET'])
# @admin_required
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_issue_slip(request, assignment_id):
    try:
        assignment = Assignment.objects.get(id = assignment_id)
        serializer = AssignmentSerializer(assignment, many=False)
        if assignment:
            assignment_data = serializer.data
            issue_slip_object = make_slip(assignment_data, assignment.issue_person_name, assignment.issue_person_code)
            # if request.user.is_authenticated:
            user = User.objects.get(username = assignment.created_by)
            issue_slip_object.iss_emp_name = f'{user.first_name} {user.last_name}' 
            issue_slip_object.iss_emp_num = user.employee_number
            issue_slip_object.iss_office = user.office_name
            return render(request, 'inventory_issue_format.html', context=slip_to_dict(issue_slip_object))
            # else:
            #     raise CustomError("User is not authenticated.")
        else:
            return JsonResponse({'status' : 'error', 'message' : 'No assignment found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)
    except CustomError as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=400)
    except Equipment.DoesNotExist:
        return JsonResponse({'status' : 'error', 'message' : 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
# @admin_required
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_return_slip(request, assignment_id):
    try:
        assignment = Assignment.objects.get(id = assignment_id)
        serializer = AssignmentSerializer(assignment, many=False)
        if assignment:
            assignment_data = serializer.data
            return_slip_object = make_slip(assignment_data,assignment.return_person_name,assignment.return_person_code)
            # if request.user.is_authenticated:
            user = User.objects.get(username = assignment.updated_by)
            return_slip_object.iss_emp_name = f'{user.first_name} {user.last_name}' 
            return_slip_object.iss_emp_num = user.employee_number
            return_slip_object.iss_office = user.office_name
            return render(request, 'inventory_return_format.html', context=slip_to_dict(return_slip_object))
            # else:
            #     raise CustomError("User is not authenticated.")
        else:
            return JsonResponse({'status' : 'error', 'message' : 'No assignment found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)
    except CustomError as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=400)
    except Assignment.DoesNotExist:
        return JsonResponse({'status' : 'error','message': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'status' : 'error','message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_assignment_history(request, equipment_id=None):
    try:
        serial_number = request.GET.get('serial_number')

        # Build the query using Q objects for optional filtering
        filters = Q()
        if serial_number:
            filters &= Q(serial_number=serial_number)
        
        if equipment_id:
            filters &= Q(id=equipment_id)

        # Query the Equipment model with the constructed filters
        equipment_list = Equipment.objects.filter(filters)
        # serializer = EquipmentSerializer(equipment_list, many=False)
        if len(equipment_list) > 1:
            raise CustomError('Multiple equipment found matching the criteria')
        elif len(equipment_list) == 0:
            raise CustomError('Equipment not exist in inventory.')
        elif len(equipment_list) == 1:
            equipment_id = equipment_list[0].id
            assignment_history = Assignment.get_assignment_history(equipment_id).order_by('id')
            if assignment_history.exists():
                assignment_history_json = list(assignment_history.values())
                return JsonResponse(assignment_history_json, status=status.HTTP_200_OK, safe=False)
            else:
                return JsonResponse({'status' : 'error', 'message' : 'No assignment found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)

    except CustomError as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error','message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_assignment_history_by_assignee(request):
    try:
        assigned_type = request.GET.get('assigned_type')
        assigned_to = request.GET.get('assigned_to')

        if assigned_to is None or assigned_type is None:
            raise CustomError('Type and Code must be present.')
        # Query the Equipment model with the constructed filters
        assignment_history_list = Assignment.objects.filter(assigned_type = assigned_type,assigned_to = assigned_to).order_by('-id')
        serializer = AssignmentSerializer(assignment_history_list, many=True)
        # serializer = EquipmentSerializer(equipment_list, many=False)
        if len(assignment_history_list) == 0:
            raise CustomError('No Equipment assigned in location or employee.')
        
        # assignment_history_json = list(assignment_history_list.values())
        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

    except CustomError as e:
        return JsonResponse({'status' : 'error', 'message' : str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error','message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_employee_retirement_info(request):
    try:
        
        result = fetch_employee_retirement_info()

        return JsonResponse(result, status=status.HTTP_200_OK, safe=False)

    except Exception as e:
        return JsonResponse({'status': 'error','message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
def make_slip(assignment_data,auth_person_name,auth_person_code):
    issue_slip_object = IssueSlip()
    issue_slip_object.set_item_name(f'{assignment_data['equipment']['category']} || {assignment_data['equipment']['sub_category']} || {assignment_data['equipment']['make']} || {assignment_data['equipment']['model']}')
    issue_slip_object.set_gen_date(datetime.now().strftime('%d %b %Y %I:%M %p'))
    issue_slip_object.set_serial_number(assignment_data['equipment']['serial_number'])
    issue_slip_object.set_remark(assignment_data['notes'])
    issue_slip_object.set_auth_person_name(auth_person_name=auth_person_name)
    issue_slip_object.set_auth_person_code(auth_person_code=auth_person_code)
    issue_slip_object
    if assignment_data['assigned_type'] == 'location' and assignment_data['assigned_to']:
        issue_slip_object.set_rec_emp_num('')
        issue_slip_object.set_rec_emp_name('')
        location_obj = Location.objects.get(location_code = assignment_data['assigned_to'])
        issue_slip_object.set_rec_office(f'{location_obj.location_name} || {location_obj.location_code}')
    elif assignment_data['assigned_type'] == 'employee' and assignment_data['assigned_to']:
        employee_obj = Employee.objects.get(employee_number = assignment_data['assigned_to'])
        issue_slip_object.set_rec_emp_num(employee_obj.employee_number)
        issue_slip_object.set_rec_emp_name(employee_obj.employee_name)
        issue_slip_object.set_rec_office('')
    else:
        issue_slip_object.set_rec_emp_num('')
        issue_slip_object.set_rec_emp_name('')
        issue_slip_object.set_rec_office('')
    return issue_slip_object
    #set issuing user info


def slip_to_dict(issue_slip):
    return {
        'item_name': issue_slip.item_name,
        'gen_date': issue_slip.gen_date,
        'serial_number': issue_slip.serial_number,
        'remark': issue_slip.remark,
        'rec_emp_num': issue_slip.rec_emp_num,
        'rec_emp_name': issue_slip.rec_emp_name,
        'rec_office': issue_slip.rec_office,
        'iss_emp_num': issue_slip.iss_emp_num,
        'iss_emp_name': issue_slip.iss_emp_name,
        'iss_office': issue_slip.iss_office,
        'auth_person_name' : issue_slip.auth_person_name,
        'auth_person_code' : issue_slip.auth_person_code
    }


@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])      
def get_assignment_overview(request):
    try:
        # Assigned vs available equipment
        assigned_count = Equipment.objects.filter(assignment_id__isnull=False).count()
        available_count = Equipment.objects.filter(assignment_id__isnull=True).count()
        
        # Top assignees (by assignment count)
        top_assignees = Assignment.objects.filter(return_date=None).values('assigned_type','assigned_to','assigned_to_details').annotate(count=Count('id')).order_by('-count')[:5]
        #top_assignee_json = json.dumps(list(top_assignees))
        
        # Recent assignments
        recent_assignments = Assignment.objects.filter(return_date=None).order_by('-created_on')[:10]
        recent_assignments_serializer = AssignmentSerializer(recent_assignments, many=True)
        
        overview = {
            'assigned_count': assigned_count,
            'available_count': available_count,
            'top_assignees': list(top_assignees),
            # 'recent_assignments': recent_assignments_strings
            'recent_assignments' : recent_assignments_serializer.data
        }
        return JsonResponse({'data': overview}, status=200,safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
