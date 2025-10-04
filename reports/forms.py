from django import forms
from django.utils import timezone
from .models import Report


class ReportForm(forms.ModelForm):
   date = forms.DateField(
        initial=timezone.now().strftime('%d/%m/%Y'),
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'type': 'text',                 # keep it text for JS picker
            'class': 'form-control date-picker',
            'placeholder': 'DD/MM/YYYY',
        })
    )
   class Meta:
        model = Report
        fields = [
            'date',
            'id_number',
            'exam_name',
            'exam_type',
            'referred_by',
            'sonologist',
            'total_ultra',
            'notes'
        ]
        widgets = {
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patient ID'}),
            'exam_name': forms.Select(attrs={'class': 'form-select'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'referred_by': forms.Select(attrs={'class': 'form-select'}),
            'sonologist': forms.Select(attrs={'class': 'form-select'}),
            'total_ultra': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


    

class ReportFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control date-picker',
            'placeholder': 'DD/MM/YYYY'
        })
    )
    end_date = forms.DateField(
        required=False,
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control date-picker',
            'placeholder': 'DD/MM/YYYY'
        })
    )
    referred_by = forms.ChoiceField(
        required=False,
        choices=[('', 'All Doctors')] + Report.REFERRED_BY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sonologist = forms.ChoiceField(
        required=False,
        choices=[('', 'All Sonologists')] + Report.SONOLOGIST_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    exam_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Exam Types')] + Report.EXAM_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    exam_name = forms.ChoiceField(
        required=False,
        choices=[('', 'All Exam Names')] + Report.EXAM_NAME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    group_by = forms.ChoiceField(
        required=False,
        choices=[
            ('', '--- Group By ---'),
            ('daily', 'Daily Report by Doctor'),
            ('monthly_sonologist', 'Monthly Report by Sonologist'),
            ('doctor', 'Raw Group by Doctor'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )




class DailyReportFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control date-picker',
            'placeholder': 'DD/MM/YYYY'
        })
    )
    end_date = forms.DateField(
        required=False,
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control date-picker',
            'placeholder': 'DD/MM/YYYY'
        })
    )
    referred_by = forms.ChoiceField(
        required=False,
        choices=[('', 'All Doctors')] + Report.REFERRED_BY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

from django import forms
from .models import Report

class MonthlyReportFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control date-picker',
            'placeholder': 'DD/MM/YYYY'
        })
    )
    end_date = forms.DateField(
        required=False,
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control date-picker',
            'placeholder': 'DD/MM/YYYY'
        })
    )
    sonologist = forms.ChoiceField(
        required=False,
        choices=[('', 'All Sonologists')] + Report.SONOLOGIST_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # exam_type = forms.ChoiceField(
    #     required=False,
    #     choices=[('', 'All Exam Types')] + Report.EXAM_TYPE_CHOICES,
    #     widget=forms.Select(attrs={'class': 'form-select'})
    # )
    # exam_name = forms.ChoiceField(
    #     required=False,
    #     choices=[('', 'All Exam Names')] + Report.EXAM_NAME_CHOICES,
    #     widget=forms.Select(attrs={'class': 'form-select'})
    # )