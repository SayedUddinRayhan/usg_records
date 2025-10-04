from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO
import openpyxl
from xhtml2pdf import pisa

from .models import Report
from .forms import ReportForm, ReportFilterForm


# 🏠 Home / Add New Report
class HomeView(View):
    template_name = "reports/home.html"

    def get(self, request):
        form = ReportForm()
        reports = Report.objects.order_by('-date')[:10]
        return render(request, self.template_name, {"form": form, "reports": reports})

    def post(self, request):
        form = ReportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("reports:home")
        reports = Report.objects.order_by('-date')[:10]
        return render(request, self.template_name, {"form": form, "reports": reports})


# 📋 Report List with aggregation
class ReportListView(View):
    template_name = "reports/report_list.html"

    def get(self, request):
        form = ReportFilterForm(request.GET or None)
        qs = Report.objects.all().order_by('-date')

        # Apply filters
        if form.is_valid():
            sd = form.cleaned_data.get("start_date")
            ed = form.cleaned_data.get("end_date")
            referred_by = form.cleaned_data.get("referred_by")
            sonologist = form.cleaned_data.get("sonologist")

            if sd:
                qs = qs.filter(date__gte=sd)
            if ed:
                qs = qs.filter(date__lte=ed)
            if referred_by:
                qs = qs.filter(referred_by=referred_by)
            if sonologist:
                qs = qs.filter(sonologist=sonologist)

        # ✅ Main Reports Pagination
        paginator_reports = Paginator(qs, 10)
        page_number_reports = request.GET.get("page_reports")
        page_obj_reports = paginator_reports.get_page(page_number_reports)

        # Daily report by doctor
        daily_by_doctor = qs.annotate(day=TruncDay('date')) \
                            .values('day', 'referred_by') \
                            .annotate(total_usg=Sum('total_ultra')) \
                            .order_by('day')

        paginator_daily = Paginator(daily_by_doctor, 15) 
        page_number_daily = request.GET.get("page_daily")
        page_obj_daily = paginator_daily.get_page(page_number_daily)

        # Monthly report by sonologist
        monthly_by_sonologist = qs.annotate(month=TruncMonth('date')) \
                                  .values('month', 'sonologist') \
                                  .annotate(total_usg=Sum('total_ultra')) \
                                  .order_by('month')

        paginator_monthly = Paginator(monthly_by_sonologist, 15)
        page_number_monthly = request.GET.get("page_monthly")
        page_obj_monthly = paginator_monthly.get_page(page_number_monthly)

        context = {
            "form": form,
            "reports": page_obj_reports,
            "daily_by_doctor": page_obj_daily,
            "monthly_by_sonologist": page_obj_monthly,
        }
        return render(request, self.template_name, context)


# 📤 Export Reports (Excel / PDF)
class ExportView(View):
    """Export reports as PDF or Excel with grouping."""

    def get(self, request, fmt):
        qs, group_by = self.get_filtered_queryset(request)

        if fmt.lower() == "xlsx":
            return self.export_xlsx(qs, group_by)
        elif fmt.lower() == "pdf":
            return self.export_pdf(qs, group_by)
        return HttpResponse(f"Unknown export format: {fmt}", status=400)

    def get_filtered_queryset(self, request):
        form = ReportFilterForm(request.GET or None)
        qs = Report.objects.all().order_by('-date')
        group_by = None

        if form.is_valid():
            sd = form.cleaned_data.get("start_date")
            ed = form.cleaned_data.get("end_date")
            referred_by = form.cleaned_data.get("referred_by")
            sonologist = form.cleaned_data.get("sonologist")
            group_by = form.cleaned_data.get("group_by")

            if sd:
                qs = qs.filter(date__gte=sd)
            if ed:
                qs = qs.filter(date__lte=ed)
            if referred_by:
                qs = qs.filter(referred_by=referred_by)
            if sonologist:
                qs = qs.filter(sonologist=sonologist)

        return qs, group_by

    def get_export_data(self, qs, group_by=None):
        rows = []

        if group_by == "daily":
            headers = ['Date', 'Referred By', 'Total USG']
            data = qs.annotate(day=TruncDay('date')) \
                     .values('day', 'referred_by') \
                     .annotate(total_usg=Sum('total_ultra')) \
                     .order_by('day')
            for r in data:
                rows.append([r['day'].strftime("%d-%m-%Y"), r['referred_by'], r['total_usg']])

        elif group_by == "monthly_sonologist":
            headers = ['Month', 'Sonologist', 'Total USG']
            data = qs.annotate(month=TruncMonth('date')) \
                     .values('month', 'sonologist') \
                     .annotate(total_usg=Sum('total_ultra')) \
                     .order_by('month')
            for r in data:
                rows.append([r['month'].strftime("%B %Y"), r['sonologist'], r['total_usg']])

        elif group_by == "doctor":
            headers = ['Referred By', 'Patient ID', 'Exam Name', 'Exam Type', 'Sonologist', 'Total Ultra']
            data = qs.values('referred_by', 'id_number', 'exam_name', 'exam_type', 'sonologist') \
                     .annotate(total_ultra=Sum('total_ultra')) \
                     .order_by('referred_by')
            for r in data:
                rows.append([
                    r['referred_by'],
                    r['id_number'],
                    r['exam_name'],
                    r['exam_type'],
                    r['sonologist'],
                    r['total_ultra']
                ])

        else:  # Raw export
            headers = ['ID', 'Date', 'Patient ID', 'Exam Name', 'Exam Type', 'Referred By', 'Sonologist', 'Total Ultra']
            for r in qs:
                rows.append([
                    r.id,
                    r.date.strftime("%d-%m-%Y"),
                    r.id_number,
                    r.exam_name,
                    r.exam_type,
                    r.referred_by,
                    r.sonologist,
                    r.total_ultra
                ])

        return headers, rows

    def export_xlsx(self, qs, group_by=None):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "USG Reports"

        headers, data = self.get_export_data(qs, group_by)
        ws.append(headers)
        for row in data:
            ws.append(row)

        for col in ws.columns:
            max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_length + 2

        filename = f"usg_reports_{group_by or 'all'}.xlsx"
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        wb.save(response)
        return response

    def export_pdf(self, qs, group_by=None):
        headers, data = self.get_export_data(qs, group_by)

        template = get_template('reports/report_pdf.html')
        html = template.render({
            'headers': headers,
            'rows': data,
            'group_by': group_by
        })

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if pdf.err:
            return HttpResponse("Error generating PDF", status=500)

        filename = f"usg_reports_{group_by or 'all'}.pdf"
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
