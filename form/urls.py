from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    path('submit/', views.save_forms, name='save_forms'),
    # Add a path for the success page if needed
    path('success/', views.success_view, name='success_page'),
    
]
