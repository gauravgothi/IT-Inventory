from datetime import datetime
from functools import wraps
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from users.models import User
from .serializers import LoginSerializer, UserSerializer
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


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

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token = serializer.get_token(user)
            return Response(token, status=status.HTTP_200_OK)
            #return render(request, 'login_success.html', {'token': token})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        #return render(request, 'login_failed.html', {'errors': serializer.errors})

@login_required()
def home(request):
    return render(request,'home.html')

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@csrf_exempt
@api_view(["POST"])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_user(request):
    try:
        data = json.loads(request.body)
        user = User.objects.create(
            username=data.get('username'),
            employee_number=data.get('employee_number'),
            office_name=data.get('office_name'),
            password=data.get('password'),
            role=data.get('role'),
            status=data.get('status'),
            remark=data.get('remark'),
            enabled=data.get('enabled', True),
            email=data.get('email'),
            mobile_no=data.get('mobile_no'),
            created_by=datetime.now(),
            created_on=datetime.now()
        )
        user.set_password(data.get('password'))  # Hash the password
        user.save()

        return JsonResponse({'status': 'success', 'message': 'User added successfully.'}, status=201)
        #return render(request, 'add_user_success.html', {'message': 'User added successfully.'})
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing field: {e.args[0]}'}, status=400)
        #return render(request, 'error.html', {'message': f'Missing field: {e.args[0]}'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        #return render(request, 'error.html', {'message': str(e)})


@api_view(["PUT"])
@admin_required
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def update_user(request, username):
    try:
        data = json.loads(request.body)
        user = User.objects.get(username=username)

        # user.username = data.get('username', user.username)
        user.role = data.get('role', user.role)
        user.status = data.get('status', user.status)
        user.remark = data.get('remark', user.remark)
        user.enabled = data.get('enabled', user.enabled)
        user.email = data.get('email', user.email)
        user.mobile_no = data.get('mobile_no', user.mobile_no)

        user.updated_by = request.user.username
        user.updated_on = datetime.now()

        if 'password' in data:
            user.set_password(data.get('password'))

        user.save()

        return JsonResponse({'status': 'success', 'message': 'User updated successfully.'}, status=200)
        #return render(request, 'update_user_success.html', {'message': 'User updated successfully.'})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
        #return render(request, 'error.html', {'message': 'User not found.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        #return render(request, 'error.html', {'message': str(e)})

@api_view(["PUT"])
@admin_required
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def deactivate_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.enabled = False
        user.save()

        return JsonResponse({'status': 'success', 'message': 'User deactivated successfully.'}, status=200)
        #return render(request, 'deactivate_user_success.html', {'message': 'User deactivated successfully.'})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
        #return render(request, 'error.html', {'message': 'User not found.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        #return render(request, 'error.html', {'message': str(e)})
    

@api_view(['GET'])
@admin_required
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])  # Ensures the user must be authenticated to access this view
def get_user(request, username):
    try:
        # Retrieve the user by username
        user = User.objects.get(username=username)
        
        # Serialize the user data
        serializer = UserSerializer(user)
        
        # Return the serialized data
        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)
        #return render(request, 'get_user.html', {'user': serializer.data})
    
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        #return render(request, 'error.html', {'message': 'User not found'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        #return render(request, 'error.html', {'message': str(e)})