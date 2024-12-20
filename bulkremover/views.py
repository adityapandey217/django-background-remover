# views.py
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import ImageUpload
from .tasks import process_image
import os
import zipfile
from django.conf import settings
from django.shortcuts import redirect
from io import BytesIO

@ensure_csrf_cookie
def index(request):
    return render(request, 'bulkremover/upload_images.html')

@require_http_methods(["POST"])
def upload_images(request):
    try:
        files = request.FILES.getlist('images')
        uploaded_images = []

        for file in files:
            image_obj = ImageUpload.objects.create(
                original_image=file, status='Pending'
            )
            uploaded_images.append({'id': image_obj.id, 'name': file.name})
            process_image.delay(image_obj.id)

        return JsonResponse({
            'status': 'success',
            'message': f"{len(files)} images uploaded successfully",
            'images': uploaded_images
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_images(request):
    try:
        images = ImageUpload.objects.all().order_by('-uploaded_at')
        images_data = [
            {
                'id': img.id,
                'original_image': img.original_image.url,
                'processed_image': img.processed_image.url if img.processed_image else None,
                'status': img.status,
                'created_at': img.uploaded_at.isoformat(),
                'name': os.path.basename(img.original_image.name)
            }
            for img in images
        ]
        return JsonResponse({'status': 'success', 'images': images_data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_http_methods(["POST"])
def delete_image(request, id):
    try:
        get_object_or_404(ImageUpload, id=id).delete()
        return JsonResponse({'status': 'success', 'message': 'Image deleted successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def download_image(request, id):
    try:
        image = get_object_or_404(ImageUpload, id=id)
        if not image.processed_image:
            return JsonResponse({'status': 'error', 'message': 'Processed image not found'}, status=404)
        return FileResponse(
            open(image.processed_image.path, 'rb'),
            as_attachment=True,
            filename=os.path.basename(image.processed_image.path)
        )
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def download_all_processed(request):
    try:
        images = ImageUpload.objects.filter(status='Complete')
        if not images.exists():
            return redirect('bulkremover:index')

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for img in images:
                zip_file.write(img.processed_image.path, os.path.basename(img.processed_image.path))

        zip_buffer.seek(0)

        return FileResponse(
            zip_buffer,
            as_attachment=True,
            filename='processed_images.zip'
        )

    except FileNotFoundError as e:
        return JsonResponse({'status': 'error', 'message': 'File not found: ' + str(e)}, status=404)
    except zipfile.BadZipFile as e:
        return JsonResponse({'status': 'error', 'message': 'Invalid ZIP file: ' + str(e)}, status=500)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_http_methods(["POST"])
def delete_all_images(request):
    try:
        ImageUpload.objects.all().delete()
        return JsonResponse({'status': 'success', 'message': 'All images deleted successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)