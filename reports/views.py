from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import render_to_string
import tempfile
import openpyxl
from openpyxl.utils import get_column_letter
from .models import Report
from .forms import ReportForm, ReportFilterForm
from xhtml2pdf import pisa
from django.template.loader import get_template
from io import BytesIO

# 🏠 Home / Add New Report
# 🏠 Home View (unchanged)
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
                qs = qs.filter(referred_by__icontains=referred_by)
            if sonologist:
                qs = qs.filter(sonologist__icontains=sonologist)

        # Aggregations
        reports = []
        if group_by == "daily" and referred_by:
            reports = qs.values('date', 'referred_by') \
                        .annotate(total_ultra=Sum('total_ultra')) \
                        .order_by('date')
        elif group_by == "monthly" and referred_by:
            reports = qs.extra(select={"month": "strftime('%%Y-%%m', date)"}) \
                        .values('month', 'referred_by') \
                        .annotate(total_ultra=Sum('total_ultra')) \
                        .order_by('month')
        elif group_by == "monthly" and sonologist:
            reports = qs.extra(select={"month": "strftime('%%Y-%%m', date)"}) \
                        .values('month', 'sonologist') \
                        .annotate(total_ultra=Sum('total_ultra')) \
                        .order_by('month')
        else:
            reports = qs

        total_ultra = qs.aggregate(total=Sum('total_ultra'))['total'] or 0

        context = {
            "form": form,
            "reports": reports,
            "group_by": group_by,
            "total_ultra": total_ultra,
        }
        return render(request, self.template_name, context)


class ExportView(View):
    """Export reports as PDF, Excel (XLSX), or Print, respecting current filters and grouping."""

    def get(self, request, fmt):
        # Get filtered queryset
        qs, group_by = self.get_filtered_queryset(request)

        if fmt.lower() == "xlsx":
            return self.export_xlsx(qs, group_by)
        elif fmt.lower() == "pdf":
            return self.export_pdf(qs, group_by)
        else:
            return HttpResponse(f"Unknown export format: {fmt}", status=400)

    def get_filtered_queryset(self, request):
        """Return filtered queryset and current grouping based on GET params."""
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
                qs = qs.filter(referred_by__icontains=referred_by)
            if sonologist:
                qs = qs.filter(sonologist__icontains=sonologist)

        return qs, group_by

    def export_xlsx(self, qs, group_by=None):
        """Export filtered reports to Excel (XLSX)."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "USG Reports"

        # Determine headers and data
        headers, data = self.get_export_data(qs, group_by)
        ws.append(headers)

        for row in data:
            ws.append(row)

        # Auto-fit column widths
        for col in ws.columns:
            max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_length + 2

        # Prepare response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=usg_reports.xlsx'
        wb.save(response)
        return response

    def export_pdf(self, qs, group_by=None):
        """Export filtered reports to PDF using template."""
        total_ultra = qs.aggregate(total=Sum('total_ultra'))['total'] or 0
        template = get_template('reports/report_pdf.html')
        html = template.render({
            'reports': qs,
            'group_by': group_by,
            'total_ultra': total_ultra,  # pass total to template
        })

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if pdf.err:
            return HttpResponse("Error generating PDF", status=500)

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="usg_reports.pdf"'
        return response

    def get_export_data(self, qs, group_by=None):
        """Return headers and rows for Excel export based on grouping."""
        rows = []

        if group_by == "daily":
            headers = ['Date', 'Referred By', 'Total Ultra']
            data = qs.values('date', 'referred_by').annotate(total_ultra=Sum('total_ultra')).order_by('date')
            for r in data:
                rows.append([r['date'].strftime("%d-%m-%Y"), r['referred_by'], r['total_ultra']])
        elif group_by == "monthly":
            headers = ['Month', 'Referred By', 'Total Ultra']
            data = qs.extra(select={"month": "strftime('%%Y-%%m', date)"}).values('month', 'referred_by').annotate(total_ultra=Sum('total_ultra')).order_by('month')
            for r in data:
                rows.append([r['month'], r['referred_by'], r['total_ultra']])
        elif group_by == "doctor":
            headers = ['Referred By', 'Patient', 'Type', 'Sonologist', 'Total Ultra']
            data = qs.values('referred_by', 'patient_name', 'type_of_usg', 'sonologist').annotate(total_ultra=Sum('total_ultra')).order_by('referred_by')
            for r in data:
                rows.append([r['referred_by'], r['patient_name'], r['type_of_usg'], r['sonologist'], r['total_ultra']])
        else:
            # Raw report export
            headers = ['ID', 'Date', 'Patient', 'Type', 'Referred By', 'Sonologist', 'Total Ultra']
            for r in qs:
                rows.append([r.id, r.date.strftime("%d-%m-%Y"), r.patient_name, r.type_of_usg, r.referred_by, r.sonologist, r.total_ultra])

        return headers, rows
