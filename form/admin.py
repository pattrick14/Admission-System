from django.contrib import admin

# Register your models here.
from django.urls import path
from .views import export_data
from .models import Application, Student, CET_Exam, JEE_Exam, UploadDoc


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'submitted_at')
    actions = ['export_data']

    def export_data(self, request, queryset):
        return export_data(request)

admin.site.register(Application, ApplicationAdmin)

urlpatterns = [
    path('admin/export-data/', export_data, name='export_data'),
]


