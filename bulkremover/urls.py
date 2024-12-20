# urls.py
from django.urls import path
from . import views

app_name = 'bulkremover'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/upload/', views.upload_images, name='upload_images'),
    path('api/images/', views.get_images, name='get_images'),
    path('api/images/<str:id>/delete/', views.delete_image, name='delete_image'),
    path('api/images/delete-all/', views.delete_all_images, name='delete_all_images'),
    path('api/images/<str:id>/download/', views.download_image, name='download_image'),
    path('api/images/download-all/', views.download_all_processed, name='download_all_processed'),
]
