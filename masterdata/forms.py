from django import forms
from .models import ExamName, ExamType, Referrer, Sonologist

INPUT_CLASS = 'form-control'

class ExamNameForm(forms.ModelForm):
    class Meta:
        model = ExamName
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Exam name (e.g. Whole Abdomen)'}),
        }

class ExamTypeForm(forms.ModelForm):
    class Meta:
        model = ExamType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Exam type (e.g. Normal)'}),
        }

class ReferrerForm(forms.ModelForm):
    class Meta:
        model = Referrer
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Doctor name'}),
        }

class SonologistForm(forms.ModelForm):
    class Meta:
        model = Sonologist
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Sonologist name'}),
        }
