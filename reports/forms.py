from django import forms
from django.utils import timezone
from .models import Report
from masterdata.models import Referrer, Sonologist, ExamName, ExamType

INPUT_CLASS = 'form-control'

class ReportForm(forms.ModelForm):
    # use DateInput with explicit format and keep input_formats for parsing
    date = forms.DateField(
        required=True,
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(
            format='%d/%m/%Y',
            attrs={
                'type': 'text',                      # keep as text so your JS date-picker (if any) works
                'class': 'form-control date-picker',
                'placeholder': 'DD/MM/YYYY',
            }
        )
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
            'id_number': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Patient ID'}),
            'exam_name': forms.Select(attrs={'class': 'form-select'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'referred_by': forms.Select(attrs={'class': 'form-select'}),
            'sonologist': forms.Select(attrs={'class': 'form-select'}),
            'total_ultra': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        """
        - Format date initial when editing an instance so the text widget shows dd/mm/YYYY.
        - Also set querysets for ModelChoiceFields as before.
        """
        super().__init__(*args, **kwargs)

        # If editing an existing instance, show date as dd/mm/YYYY in the text widget
        instance = kwargs.get('instance')  # update view passes instance via kwargs normally
        if instance and getattr(instance, 'date', None):
            # set initial so the widget renders formatted string
            self.initial['date'] = instance.date.strftime('%d/%m/%Y')

        # fallback: for new forms show today's date string (optional)
        if not self.initial.get('date'):
            self.initial['date'] = timezone.now().strftime('%d/%m/%Y')

        # model choice querysets
        self.fields['referred_by'].queryset = Referrer.active.all()
        self.fields['sonologist'].queryset = Sonologist.active.all()
        self.fields['exam_name'].queryset = ExamName.active.all()

        # make mandatory fields required
        self.fields['exam_name'].required = True
        self.fields['exam_type'].required = True
        self.fields['sonologist'].required = True


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
    referred_by = forms.ModelChoiceField(
        required=False,
        queryset=Referrer.active.all(),
        empty_label="All Doctors",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sonologist = forms.ModelChoiceField(
        required=False,
        queryset=Sonologist.active.all(),
        empty_label="All Sonologists",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    exam_type = forms.ModelChoiceField(
        required=False,
        queryset=ExamType.active.all(),
        empty_label="All Exam Types",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    exam_name = forms.ModelChoiceField(
        required=False,
        queryset=ExamName.active.all(),
        empty_label="All Exam Names",
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
    referred_by = forms.ModelChoiceField(
        required=False,
        queryset=Referrer.active.all(),
        empty_label="All Doctors",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class ExamTypeReportFilterForm(forms.Form):
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
    sonologist = forms.ModelChoiceField(
        queryset=Sonologist.active.all(), required=False, empty_label="All"
    )
    exam_type = forms.ModelChoiceField(
        queryset=ExamType.active.all(), required=False, empty_label="All"
    )

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
    sonologist = forms.ModelChoiceField(
        required=False,
        queryset=Sonologist.active.all(),
        empty_label="All Sonologists",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
