from urllib import request
from django.test import TestCase

from django.shortcuts import render
from django.views import View
from .models import Report
from .forms import ReportFilterForm
from .utils.export import export_reports_xlsx, export_reports_pdf
from django.db.models import Count
from django.http import HttpResponse
from django.utils.dateparse import parse_date


class ReportListView(View):
    template_name = 'reports/report_list.html'


    def get(self, request):
        form = ReportFilterForm(request.GET or None)
        qs = Report.objects.all()
        if form.is_valid():
            sd = form.cleaned_data.get('start_date')
            ed = form.cleaned_data.get('end_date')
            if sd:
                qs = qs.filter(date__gte=sd)
            if ed:
                qs = qs.filter(date__lte=ed)
            if form.cleaned_data.get('referred_by'):
                qs = qs.filter(referred_by__icontains=form.cleaned_data['referred_by'])
            if form.cleaned_data.get('sonologist'):
                qs = qs.filter(sonologist__icontains=form.cleaned_data['sonologist'])


    # simple aggregation examples
        daily_by_ref = qs.values('date','referred_by').annotate(count=Count('id'))


        context = {'form': form, 'reports': qs, 'daily_by_ref': daily_by_ref}
        return render(request, self.template_name, context)


class ExportView(View):
    def get(self, request, fmt):
        qs = Report.objects.all()
    # apply same filters as above for GET params
    form = ReportFilterForm(request.GET or None)
    if form.is_valid():
        sd = form.cleaned_data.get('start_date')
        ed = form.cleaned_data.get('end_date')
        if sd: qs = qs.filter(date__gte=sd)
        if ed: qs = qs.filter(date__lte=ed)
        if form.cleaned_data.get('referred_by'):
            qs = qs.filter(referred_by__icontains=form.cleaned_data['referred_by'])
        if form.cleaned_data.get('sonologist'):
            qs = qs.filter(sonologist__icontains=form.cleaned_data['sonologist'])
    if fmt == 'xlsx':
        return export_reports_xlsx(qs)
    elif fmt == 'pdf':
        return export_reports_pdf(qs, request=request)
    else:
        return HttpResponse(status=400)
