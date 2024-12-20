from django.db import models
import uuid

def get_og_path(instance, filename):
    return f"{instance.id}/original/{filename}"


def get_pr_path(instance, filename):
    return f"{instance.id}/processed/{filename}"


class ImageUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_image = models.ImageField(upload_to=get_og_path)
    processed_image = models.ImageField(upload_to=get_pr_path, null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')  # Pending, Processing, Complete
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
