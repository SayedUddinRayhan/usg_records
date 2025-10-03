from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id_number','date','referred_by','sonologist','type_of_usg','total_ultra')
    list_filter = ('date','referred_by','sonologist','type_of_usg')
    search_fields = ('id_number','referred_by','sonologist','patient_name')