from celery import shared_task
from .models import ImageUpload
from rembg import remove
from PIL import Image
import io
from django.core.files.base import ContentFile

@shared_task
def process_image(image_id):
    try:
        image_obj = ImageUpload.objects.get(id=image_id)
    except ImageUpload.DoesNotExist:
        return f"Image with id {image_id} does not exist"

    try:
        image_obj.status = 'Processing'
        image_obj.save()

        input_data = image_obj.original_image.read()

        output_data = remove(input_data)

        with io.BytesIO(output_data) as output_io:
            processed_image = Image.open(output_io)
            processed_image_io = io.BytesIO()
            processed_image.save(processed_image_io, format='PNG')

        # Save the processed image
        processed_image_file = ContentFile(processed_image_io.getvalue())
        output_filename = f"{image_obj.original_image.name.split('/')[-1].split('.')[0]}.png"
        image_obj.processed_image.save(output_filename, processed_image_file)

        image_obj.status = 'Complete'
        image_obj.save()

    except Exception as e:
        image_obj.status = 'Failed'
        image_obj.save()
        return f"Error processing image with id {image_id}: {e}"

    return f"Image with id {image_id} processed successfully"
