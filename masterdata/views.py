from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse

from .models import ExamName, ExamType, Referrer, Sonologist
from .forms import ExamNameForm, ExamTypeForm, ReferrerForm, SonologistForm

# Generic helpers to reduce repetition
def _list_view(request, Model, template, context_name='items'):
    items = Model.active.all()  # Only active
    return render(request, template, {context_name: items})


def _form_view(request, form_class, template, title, redirect_name):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'{title} saved.')
            return redirect(redirect_name)
    else:
        form = form_class()
    return render(request, template, {'form': form, 'title': title})

def _edit_view(request, pk, Model, form_class, template, title, redirect_name):
    obj = get_object_or_404(Model, pk=pk)
    if request.method == 'POST':
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'{title} updated.')
            return redirect(redirect_name)
    else:
        form = form_class(instance=obj)
    return render(request, template, {'form': form, 'title': title})

def _delete_view(request, pk, Model, template, title, redirect_name):
    obj = get_object_or_404(Model, pk=pk)
    if request.method == 'POST':
        obj.is_active = False  # Soft delete
        obj.save()
        messages.success(request, f'{title} deactivated (soft deleted).')
        return redirect(redirect_name)
    return render(request, template, {'object': obj, 'title': title})



# ExamName
# @staff_member_required
def examname_list(request):
    return _list_view(request, ExamName, 'examname_list.html')

# @staff_member_required
def examname_create(request):
    return _form_view(request, ExamNameForm, 'examname_form.html', 'Exam name', 'masterdata:examname_list')

# @staff_member_required
def examname_edit(request, pk):
    return _edit_view(request, pk, ExamName, ExamNameForm, 'examname_form.html', 'Exam name', 'masterdata:examname_list')

# @staff_member_required
def examname_delete(request, pk):
    return _delete_view(request, pk, ExamName, 'confirm_delete.html', 'Exam name', 'masterdata:examname_list')



# ExamType
# @staff_member_required
def examtype_list(request):
    return _list_view(request, ExamType, 'examtype_list.html')

# @staff_member_required
def examtype_create(request):
    return _form_view(request, ExamTypeForm, 'examtype_create.html', 'Exam type', 'masterdata:examtype_list')

# @staff_member_required
def examtype_edit(request, pk):
    return _edit_view(request, pk, ExamType, ExamTypeForm, 'examtype_edit.html', 'Exam type', 'masterdata:examtype_list')

# @staff_member_required
def examtype_delete(request, pk):
    return _delete_view(request, pk, ExamType, 'confirm_delete.html', 'Exam type', 'masterdata:examtype_list')


# Referrer
# @staff_member_required
def referrer_list(request):
    return _list_view(request, Referrer, 'referrer_list.html')

# @staff_member_required
def referrer_create(request):
    return _form_view(request, ReferrerForm, 'referrer_create.html', 'Referrer', 'masterdata:referrer_list')

# @staff_member_required
def referrer_edit(request, pk):
    return _edit_view(request, pk, Referrer, ReferrerForm, 'referrer_edit.html', 'Referrer', 'masterdata:referrer_list')

# @staff_member_required
def referrer_delete(request, pk):
    return _delete_view(request, pk, Referrer, 'confirm_delete.html', 'Referrer', 'masterdata:referrer_list')


# Sonologist
# @staff_member_required
def sonologist_list(request):
    return _list_view(request, Sonologist, 'sonologist_list.html')

# @staff_member_required
def sonologist_create(request):
    return _form_view(request, SonologistForm, 'sonologist_create.html', 'Sonologist', 'masterdata:sonologist_list')

# @staff_member_required
def sonologist_edit(request, pk):
    return _edit_view(request, pk, Sonologist, SonologistForm, 'sonologist_edit.html', 'Sonologist', 'masterdata:sonologist_list')

# @staff_member_required
def sonologist_delete(request, pk):
    return _delete_view(request, pk, Sonologist, 'confirm_delete.html', 'Sonologist', 'masterdata:sonologist_list')
