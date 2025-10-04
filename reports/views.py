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
from .forms import ReportForm, ReportFilterForm, DailyReportFilterForm, MonthlyReportFilterForm
from .utils import export_to_excel, export_to_pdf


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


# 📋 Report List (Detailed / Filterable)
class ReportListView(View):
    template_name = "reports/report_list.html"

    def get(self, request):
        form = ReportFilterForm(request.GET or None)
        qs = Report.objects.all().order_by('-date')

        if form.is_valid():
            sd = form.cleaned_data.get("start_date")
            ed = form.cleaned_data.get("end_date")
            referred_by = form.cleaned_data.get("referred_by")
            sonologist = form.cleaned_data.get("sonologist")
            exam_type = form.cleaned_data.get("exam_type")
            exam_name = form.cleaned_data.get("exam_name")

            if sd: qs = qs.filter(date__gte=sd)
            if ed: qs = qs.filter(date__lte=ed)
            if referred_by: qs = qs.filter(referred_by__icontains=referred_by)
            if sonologist: qs = qs.filter(sonologist__icontains=sonologist)
            if exam_type: qs = qs.filter(exam_type__icontains=exam_type)
            if exam_name: qs = qs.filter(exam_name__icontains=exam_name)

        paginator = Paginator(qs, 10)
        page_number = request.GET.get("page")
        reports = paginator.get_page(page_number)

        return render(request, self.template_name, {"form": form, "reports": reports})


# 📅 Daily Report (Grouped by Doctor)
class DailyReportView(View):
    template_name = "reports/daily_report.html"

    def get_queryset(self, request):
        form = DailyReportFilterForm(request.GET or None)
        qs = Report.objects.all()

        if form.is_valid():
            sd = form.cleaned_data.get("start_date")
            ed = form.cleaned_data.get("end_date")
            referred_by = form.cleaned_data.get("referred_by")

            if sd: qs = qs.filter(date__gte=sd)
            if ed: qs = qs.filter(date__lte=ed)
            if referred_by: qs = qs.filter(referred_by__icontains=referred_by)

        return qs, form

    def get(self, request):
        qs, form = self.get_queryset(request)
        daily_by_doctor = (
            qs.annotate(day=TruncDay("date"))
              .values("day", "referred_by")
              .annotate(total_usg=Sum("total_ultra"))
              .order_by("-day")
        )

        paginator = Paginator(daily_by_doctor, 20)
        page = request.GET.get("page")
        page_obj = paginator.get_page(page)

        return render(request, self.template_name, {"form": form, "daily_reports": page_obj})


# 📊 Monthly Report (Grouped by Sonologist)
class MonthlyReportView(View):
    template_name = "reports/monthly_report.html"

    def get_queryset(self, request):
        form = MonthlyReportFilterForm(request.GET or None)
        qs = Report.objects.all()

        if form.is_valid():
            sd = form.cleaned_data.get("start_date")
            ed = form.cleaned_data.get("end_date")
            sonologist = form.cleaned_data.get("sonologist")
            exam_type = form.cleaned_data.get("exam_type")
            exam_name = form.cleaned_data.get("exam_name")

            if sd: qs = qs.filter(date__gte=sd)
            if ed: qs = qs.filter(date__lte=ed)
            if sonologist: qs = qs.filter(sonologist__icontains=sonologist)
            if exam_type: qs = qs.filter(exam_type__icontains=exam_type)
            if exam_name: qs = qs.filter(exam_name__icontains=exam_name)

        return qs, form

    def get(self, request):
        qs, form = self.get_queryset(request)
        monthly_by_sonologist = (
            qs.annotate(month=TruncMonth("date"))
                .values("month", "sonologist")  # remove exam_type and exam_name
                .annotate(total_usg=Sum("total_ultra"))
                .order_by("-month", "sonologist")
)

        paginator = Paginator(monthly_by_sonologist, 20)
        page = request.GET.get("page")
        page_obj = paginator.get_page(page)

        return render(request, self.template_name, {"form": form, "monthly_reports": page_obj})


class ExportView(View):
    """Export filtered reports to Excel or PDF"""
    def get(self, request, fmt):
        form = ReportFilterForm(request.GET or None)
        qs = Report.objects.all().order_by('-date')

        applied_filters = []

        if form.is_valid():
            sd = form.cleaned_data.get("start_date")
            ed = form.cleaned_data.get("end_date")
            referred_by = form.cleaned_data.get("referred_by")
            sonologist = form.cleaned_data.get("sonologist")
            exam_type = form.cleaned_data.get("exam_type")
            exam_name = form.cleaned_data.get("exam_name")

            if sd:
                qs = qs.filter(date__gte=sd)
                applied_filters.append(f"Start Date: {sd.strftime('%d-%m-%Y')}")
            if ed:
                qs = qs.filter(date__lte=ed)
                applied_filters.append(f"End Date: {ed.strftime('%d-%m-%Y')}")
            if referred_by:
                qs = qs.filter(referred_by__icontains=referred_by)
                applied_filters.append(f"Doctor: {referred_by}")
            if sonologist:
                qs = qs.filter(sonologist__icontains=sonologist)
                applied_filters.append(f"Sonologist: {sonologist}")
            if exam_type:
                qs = qs.filter(exam_type__icontains=exam_type)
                applied_filters.append(f"Exam Type: {exam_type}")
            if exam_name:
                qs = qs.filter(exam_name__icontains=exam_name)
                applied_filters.append(f"Exam Name: {exam_name}")

        headers = ['Date', 'Referred By', 'Sonologist', 'Exam Type', 'Exam Name', 'Total USG']
        rows = [
            [
                r.date.strftime("%d-%m-%Y"),
                r.referred_by,
                r.sonologist,
                r.exam_type,
                r.exam_name,
                r.total_ultra
            ]
            for r in qs
        ]

        # Calculate grand total
        grand_total_usg = qs.aggregate(total=Sum('total_ultra'))['total'] or 0

        # Append grand total row (optional for Excel)
        rows.append(['', '', '', '', 'Grand Total', grand_total_usg])

        if fmt.lower() == 'xlsx':
            return export_to_excel(rows, headers, "all_reports")
        elif fmt.lower() == 'pdf':
            return export_to_pdf(
                rows,
                headers,
                "all_reports",
                extra_context={
                    "grand_total_usg": grand_total_usg,
                    "applied_filters": applied_filters
                }
            )
        else:
            return HttpResponse("Invalid format", status=400)






# 📤 Daily Export (Excel / PDF)
class DailyReportExportView(View):
    def get(self, request, fmt):
        form = DailyReportFilterForm(request.GET or None)
        qs = Report.objects.all()

        if form.is_valid():
            sd = form.cleaned_data.get("start_date")
            ed = form.cleaned_data.get("end_date")
            referred_by = form.cleaned_data.get("referred_by")
            if sd: qs = qs.filter(date__gte=sd)
            if ed: qs = qs.filter(date__lte=ed)
            if referred_by: qs = qs.filter(referred_by__icontains=referred_by)

        daily_data = (
            qs.annotate(day=TruncDay('date'))
              .values('day', 'referred_by')
              .annotate(total_usg=Sum('total_ultra'))
              .order_by('day')
        )

        headers = ['Date', 'Referred By', 'Total USG']
        rows = [[r['day'].strftime("%d-%m-%Y"), r['referred_by'], r['total_usg']] for r in daily_data]

        # Calculate Grand Total USG
        grand_total_usg = sum(r['total_usg'] for r in daily_data)

        if fmt.lower() == 'xlsx':
            return export_to_excel(rows, headers, "daily_report")
        elif fmt.lower() == 'pdf':
            return export_to_pdf(
                rows,
                headers,
                "daily_report",
                extra_context={'grand_total_usg': grand_total_usg, 'group_by': 'daily'}
            )
        return HttpResponse("Invalid format", status=400)



# 📤 Monthly Export (Excel / PDF)
class MonthlyReportExportView(View):
    def get(self, request, fmt):
        form = MonthlyReportFilterForm(request.GET or None)
        qs = Report.objects.all()

        if form.is_valid():
            sd = form.cleaned_data.get("start_date")
            ed = form.cleaned_data.get("end_date")
            sonologist = form.cleaned_data.get("sonologist")
            if sd: qs = qs.filter(date__gte=sd)
            if ed: qs = qs.filter(date__lte=ed)
            if sonologist: qs = qs.filter(sonologist__icontains=sonologist)

        monthly_data = (
            qs.annotate(month=TruncMonth('date'))
              .values('month', 'sonologist')  # only month and sonologist
              .annotate(total_usg=Sum('total_ultra'))
              .order_by('month', 'sonologist')
        )

        headers = ['Month', 'Sonologist', 'Total USG']
        rows = [[r['month'].strftime("%B %Y"), r['sonologist'], r['total_usg']] for r in monthly_data]

        # Calculate Grand Total USG
        grand_total_usg = sum(r['total_usg'] for r in monthly_data)

        if fmt.lower() == 'xlsx':
            return export_to_excel(rows, headers, "monthly_report")
        elif fmt.lower() == 'pdf':
            return export_to_pdf(
                rows,
                headers,
                "monthly_report",
                extra_context={'grand_total_usg': grand_total_usg, 'group_by': 'monthly_sonologist'}
            )
        return HttpResponse("Invalid format", status=400)

