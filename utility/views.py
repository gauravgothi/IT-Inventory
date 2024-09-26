from datetime import datetime
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import FileResponse, Http404
from .models import Document, Spreadsheet
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

folder_path = "C:/Inventory/"

def get_file_response(file_name):
    file_path = os.path.join(folder_path, file_name)
    if not os.path.exists(file_path):
        raise Http404("File does not exist")
    file = open(file_path, 'rb')
    response = FileResponse(file)
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
    return response


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

def upload_document2(file,asignee_type,asignee_id):
    try:
        if file:
        # Ensure the file is either PDF or JPG
            if file.name.endswith('.pdf') or file.name.endswith('.jpg'):
                # Create the filename in the format location_id_datetime.extension
                extension = os.path.splitext(file.name)[1]
                datetime_str = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f'{asignee_type}_{asignee_id}_{datetime_str}{extension}'
                

                # Ensure the folder exists
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                # Define the full file path
                file_path = os.path.join(folder_path, filename)

                # Save the file manually
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                        destination.close()

                # Save the file reference to the database (optional)
                # document = Document(file=file)
                # document.save()

                return filename
            else:
                return ''
        return ''
    except BaseException as e:
            return e

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

@csrf_exempt
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
def download_file(request):
    file_name = request.GET.get('file_name')
    if file_name:
        try:
            return get_file_response(file_name)
        except Http404 as e:
            return JsonResponse({'error': str(e)}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred while processing the file'}, status=500)
    else:
        return JsonResponse({'error': 'No file path provided'}, status=400)


