from django.http import JsonResponse
from assignees.serializers import EmployeeSerializer, LocationSerializer, VendorSerializer
from .models import Assignee, Employee, Location, Vendor
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

@csrf_exempt
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_assignee_data(request, target_type, target_code):
    assignee = Assignee(target_type, target_code)
    try:
        if assignee.target_type == 'employee':
            obj = Employee.objects.get(employee_number=assignee.target_code)
            serializer = EmployeeSerializer(obj)
        elif assignee.target_type == 'location':
            obj = Location.objects.get(location_code=assignee.target_code)
            serializer = LocationSerializer(obj)
        elif assignee.target_type == 'vendor':
            obj = Vendor.objects.get(vendor_code=assignee.target_code)
            serializer = VendorSerializer(obj)
        else:
            return JsonResponse({'error': 'Invalid target_type'}, status=400)

        return JsonResponse(serializer.data, status=200)

    except (Location.DoesNotExist, Employee.DoesNotExist, Vendor.DoesNotExist):
        return JsonResponse({'error': 'Object not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


