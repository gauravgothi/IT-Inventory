from django.shortcuts import render
from django.http import JsonResponse
from .models import Document, Spreadsheet
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# View to handle PDF and JPG file uploads
@authentication_classes([TokenAuthentication])  # or JWTAuthentication
@permission_classes([IsAuthenticated])
def upload_document(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file.name.endswith('.pdf') or file.name.endswith('.jpg'):
            document = Document(file=file)
            document.save()
            return JsonResponse({'status': 'success', 'message': 'File uploaded successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid file type. Only PDF and JPG files are allowed.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

# View to handle Excel, XLS, and CSV file uploads
@authentication_classes([TokenAuthentication])  # or JWTAuthentication
@permission_classes([IsAuthenticated])
def upload_spreadsheet(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file.name.endswith('.xlsx') or file.name.endswith('.xls') or file.name.endswith('.csv'):
            spreadsheet = Spreadsheet(file=file)
            spreadsheet.save()
            return JsonResponse({'status': 'success', 'message': 'File uploaded successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid file type. Only Excel, XLS, and CSV files are allowed.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

