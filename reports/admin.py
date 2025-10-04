from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'id_number',
        'date',
        'patient_name',
        'exam_name',
        'exam_type',
        'referred_by',
        'sonologist',
        'total_ultra'
    )
    list_filter = (
        'date',
        'exam_name',
        'exam_type',
        'referred_by',
        'sonologist'
    )
    search_fields = (
        'id_number',
        'patient_name',
        'referred_by',
        'sonologist',
        'notes'
    )
