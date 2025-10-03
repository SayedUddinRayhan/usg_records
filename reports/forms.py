from django import forms
from reports.models import Report
from django.utils import timezone

class ReportForm(forms.ModelForm):
    date = forms.DateField(
        initial=timezone.now().strftime('%d/%m/%Y'),  # display DD/MM/YYYY
        input_formats=['%d/%m/%Y'],  # tell Django how to parse it
        widget=forms.TextInput(attrs={
            'type': 'text',  # must be text for custom format
            'class': 'form-control',
            'placeholder': 'DD/MM/YYYY'
        })
    )

    class Meta:
        model = Report
        fields = ['date', 'patient_name', 'type_of_usg', 'referred_by', 'sonologist', 'total_ultra', 'notes']
        widgets = {
            'patient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter patient name'}),
            'type_of_usg': forms.Select(attrs={'class': 'form-select'}),
            'referred_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Referred by'}),
            'sonologist': forms.TextInput(attrs={'class': 'form-control'}),
            'total_ultra': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

        
class ReportFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    referred_by = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Referred By Doctor'})
    )
    sonologist = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sonologist Name'})
    )
    group_by = forms.ChoiceField(
        required=False,
        choices=[
            ('', '--- Group By ---'),
            ('daily', 'Daily'),
            ('monthly', 'Monthly'),
            ('doctor', 'Referred By Doctor'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
