from django.contrib import admin
from .models import ExamName, ExamType, Referrer, Sonologist

@admin.register(ExamName)
class ExamNameAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Referrer)
class ReferrerAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)

@admin.register(Sonologist)
class SonologistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    
