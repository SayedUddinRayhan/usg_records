from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncMonth
from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO
import openpyxl
from xhtml2pdf import pisa
from django.contrib import messages
from .models import Report
from .forms import ReportForm, ReportFilterForm, DailyReportFilterForm, MonthlyReportFilterForm, ExamTypeReportFilterForm
from .utils import export_to_excel, export_to_pdf, export_pdf_grouped
from django.db.models import Sum, F
from datetime import date
from django.utils.timezone import localtime, now
from django.http import JsonResponse

# Home / Add New Report
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
            # Success message
            messages.success(request, "Report saved successfully!")
            return redirect("reports:home")
        else:
            messages.error(request, "Please correct the errors below.")
        reports = Report.objects.order_by('-date')[:10]
        return render(request, self.template_name, {"form": form, "reports": reports})

# Dashboard page (HTML)
class DashboardPageView(TemplateView):
    template_name = 'reports/dashboard.html'


class DashboardDataView(View):
    """Return live dashboard summary data as JSON (for AJAX refresh)."""

    def get(self, request, *args, **kwargs):
        today = localtime(now()).date()

        total_ultra_today = Report.objects.filter(date=today).aggregate(total=Sum('total_ultra'))['total'] or 0
        total_ultra_all = Report.objects.aggregate(total=Sum('total_ultra'))['total'] or 0

        # Exam type summary
        category_summary = list(
            Report.objects
            .filter(date=today)
            .values('exam_type__name')
            .annotate(
                report_count=Count('id'),
                ultra_sum=Sum('total_ultra')
            )
            .order_by('-report_count')
        )

        # Sonologist summary
        sonologist_summary = list(
            Report.objects
            .filter(date=today)
            .values('sonologist__name')
            .annotate(
                report_count=Count('id'),
                ultra_sum=Sum('total_ultra')
            )
            .order_by('-report_count')
        )

        return JsonResponse({
            'total_ultra_today': total_ultra_today,
            'total_ultra_all': total_ultra_all,
            'category_summary': category_summary,
            'sonologist_summary': sonologist_summary,
            'timestamp': localtime(now()).strftime("%H:%M:%S"),
        })


# Report List
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
            if referred_by: qs = qs.filter(referred_by=referred_by)
            if sonologist: qs = qs.filter(sonologist=sonologist)
            if exam_type: qs = qs.filter(exam_type__icontains=exam_type)
            if exam_name: qs = qs.filter(exam_name=exam_name)

        paginator = Paginator(qs, 10)
        page_number = request.GET.get("page")
        reports = paginator.get_page(page_number)

        return render(request, self.template_name, {"form": form, "reports": reports})


# Daily Report
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
            if referred_by: qs = qs.filter(referred_by=referred_by)

        return qs, form

    def get(self, request):
        qs, form = self.get_queryset(request)

        # Annotate the doctor name
        daily_by_doctor = (
            qs.annotate(day=TruncDay("date"))
              .values("day", "referred_by")
              .annotate(
                  referred_by_name=F("referred_by__name"),
                  total_usg=Sum("total_ultra")
              )
              .order_by("-day")
        )

        paginator = Paginator(daily_by_doctor, 20)
        page = request.GET.get("page")
        page_obj = paginator.get_page(page)

        return render(request, self.template_name, {
            "form": form,
            "daily_reports": page_obj
        })




class ExamTypeReportView(View):

    def get(self, request):
        today = date.today()

        form = ExamTypeReportFilterForm(request.GET or None)

        qs = Report.objects.select_related('sonologist', 'exam_type').all()

        # Default dates
        start_date = today
        end_date = today

        # When form receives GET
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date") or today
            end_date = form.cleaned_data.get("end_date") or today

            qs = qs.filter(date__gte=start_date, date__lte=end_date)

            sonologist = form.cleaned_data.get("sonologist")
            exam_type = form.cleaned_data.get("exam_type")

            if sonologist:
                qs = qs.filter(sonologist=sonologist)
            if exam_type:
                qs = qs.filter(exam_type=exam_type)

        # Aggregate by sonologist + exam type
        raw = (
            qs.values("sonologist__name", "exam_type__name")
              .annotate(total_usg=Sum("total_ultra"))
              .order_by("sonologist__name", "exam_type__name")
        )

        # Group by sonologist
        grouped_reports = {}
        for r in raw:
            sname = r["sonologist__name"] or "Unknown"
            if sname not in grouped_reports:
                grouped_reports[sname] = {
                    "exams": [],
                    "total_usg": 0
                }

            grouped_reports[sname]["exams"].append({
                "exam_type": r["exam_type__name"] or "Unknown",
                "total_usg": r["total_usg"]
            })

            grouped_reports[sname]["total_usg"] += r["total_usg"]

        grand_total_usg = sum(v["total_usg"] for v in grouped_reports.values())

        # --- Pagination of sonologists ---
        sonologist_list = list(grouped_reports.items())
        paginator = Paginator(sonologist_list, 10)  # 10 sonologists per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "reports/exam_type_report.html", {
            "form": form,
            "grouped_reports": page_obj,   # pass page_obj instead of full dict
            "grand_total_usg": grand_total_usg,
            "page_obj": page_obj,
            "start_date": start_date,
            "end_date": end_date,
        })








# Monthly Report (Grouped by Sonologist)
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
            if sonologist: qs = qs.filter(sonologist=sonologist)
            if exam_type: qs = qs.filter(exam_type__icontains=exam_type)
            if exam_name: qs = qs.filter(exam_name=exam_name)

        return qs, form

    def get(self, request):
        qs, form = self.get_queryset(request)

        # Annotate sonologist name
        monthly_by_sonologist = (
            qs.annotate(month=TruncMonth("date"))
              .values("month", "sonologist")
              .annotate(
                  sonologist_name=F("sonologist__name"),
                  total_usg=Sum("total_ultra")
              )
              .order_by("-month", "sonologist")
        )

        paginator = Paginator(monthly_by_sonologist, 20)
        page = request.GET.get("page")
        page_obj = paginator.get_page(page)

        return render(request, self.template_name, {
            "form": form,
            "monthly_reports": page_obj
        })


#  Export All Reports (Excel / PDF)
class ExportView(View):
    def get(self, request, fmt):
        form = ReportFilterForm(request.GET or None)
        qs = Report.objects.all().order_by('-date')
        applied_filters = []

        if form.is_valid():
            sd = form.cleaned_data.get("start_date")
            ed = form.cleaned_data.get("end_date")
            referred_by = form.cleaned_data.get("referred_by_name")
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
                qs = qs.filter(referred_by=referred_by)
                applied_filters.append(f"Doctor: {referred_by}")
            if sonologist:
                qs = qs.filter(sonologist=sonologist)
                applied_filters.append(f"Sonologist: {sonologist}")
            if exam_type:
                qs = qs.filter(exam_type=exam_type)
                applied_filters.append(f"Exam Type: {exam_type}")
            if exam_name:
                qs = qs.filter(exam_name__icontains=exam_name)
                applied_filters.append(f"Exam Name: {exam_name}")

        # Annotate names for export
        qs = qs.annotate(
            referred_by_name=F('referred_by__name'),
            sonologist_name=F('sonologist__name')
        )

        headers = ['Date', 'Referred By', 'Sonologist', 'Exam Type', 'Exam Name', 'Total USG']
        rows = [
            [
                r.date.strftime("%d-%m-%Y"),
                getattr(r, 'referred_by_name', r.referred_by),
                getattr(r, 'sonologist_name', r.sonologist),
                r.exam_type,
                r.exam_name,
                r.total_ultra
            ]
            for r in qs
        ]

        grand_total_usg = qs.aggregate(total=Sum('total_ultra'))['total'] or 0
        rows.append(['', '', '', '', 'Grand Total', grand_total_usg])

        if fmt.lower() == 'xlsx':
            return export_to_excel(rows, headers, "all_reports")
        elif fmt.lower() == 'pdf':
            return export_to_pdf(rows, headers, "all_reports", extra_context={
                "grand_total_usg": grand_total_usg,
                "applied_filters": applied_filters
            })
        return HttpResponse("Invalid format", status=400)


#  Daily Export (Excel / PDF)
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
            if referred_by: qs = qs.filter(referred_by=referred_by)

        daily_data = (
            qs.annotate(day=TruncDay('date'))
              .values('day', 'referred_by')
              .annotate(
                  referred_by_name=F('referred_by__name'),
                  total_usg=Sum('total_ultra')
              )
              .order_by('day')
        )

        headers = ['Date', 'Referred By', 'Total USG']
        rows = [[r['day'].strftime("%d-%m-%Y"), r['referred_by_name'], r['total_usg']] for r in daily_data]

        grand_total_usg = sum(r['total_usg'] for r in daily_data)

        if fmt.lower() == 'xlsx':
            return export_to_excel(rows, headers, "daily_report")
        elif fmt.lower() == 'pdf':
            return export_to_pdf(rows, headers, "daily_report", extra_context={
                'grand_total_usg': grand_total_usg, 'group_by': 'daily'
            })
        return HttpResponse("Invalid format", status=400)

class ExamTypeReportExportView(View):
    """Export exam-type-wise USG report by sonologist (Excel / PDF)."""

    def get(self, request, fmt):
        today = date.today()
        form = ExamTypeReportFilterForm(request.GET or None)

        # Default date range
        sd = today
        ed = today
        sonologist = None
        exam_type = None

        if form.is_valid():
            sd = form.cleaned_data.get("start_date") or today
            ed = form.cleaned_data.get("end_date") or today
            sonologist = form.cleaned_data.get("sonologist")
            exam_type = form.cleaned_data.get("exam_type")

        # Text for header
        filter_range_text = f"Showing data from {sd.strftime('%d-%m-%Y')} to {ed.strftime('%d-%m-%Y')}"

        # Base queryset
        qs = Report.objects.select_related("sonologist", "exam_type").filter(
            date__gte=sd,
            date__lte=ed
        )

        # Optional filters
        if sonologist:
            qs = qs.filter(sonologist=sonologist)
        if exam_type:
            qs = qs.filter(exam_type=exam_type)

        # Aggregate totals
        db_rows = (
            qs.values("sonologist", "exam_type")
              .annotate(
                  sonologist_name=F("sonologist__name"),
                  exam_type_name=F("exam_type__name"),
                  total_usg=Sum("total_ultra"),
              )
              .order_by("sonologist__name", "exam_type__name")
        )

        # Grouping
        grouped_data = {}
        for r in db_rows:
            sname = r["sonologist_name"] or "Unknown"

            if sname not in grouped_data:
                grouped_data[sname] = {
                    "exams": [],
                    "total_usg": 0,
                }

            grouped_data[sname]["exams"].append({
                "exam_type": r["exam_type_name"] or "Unknown",
                "total_usg": r["total_usg"],
            })

            grouped_data[sname]["total_usg"] += r["total_usg"]

        # Prepare export rows
        rows = []
        for sname, data in grouped_data.items():
            first = True
            for exam in data["exams"]:
                rows.append([
                    sname if first else "",
                    exam["exam_type"],
                    exam["total_usg"],
                ])
                first = False

            # Total under each sonologist
            rows.append(["", "Total USG:", data["total_usg"]])

        # Grand total
        grand_total_usg = sum(d["total_usg"] for d in grouped_data.values())
        rows.append(["", "Grand Total USG:", grand_total_usg])

        headers = ["Sonologist", "Exam Type", "Total USG"]

        # Export Excel
        if fmt.lower() == "xlsx":
            return export_to_excel(rows, headers, "exam_type_report")

        # Export PDF
        if fmt.lower() == "pdf":
            return export_pdf_grouped(
                grouped_data,
                headers,
                "exam_type_report",
                extra_context={
                    "grand_total_usg": grand_total_usg,
                    "filter_range_text": filter_range_text,
                },
            )

        return HttpResponse("Invalid format", status=400)




#  Monthly Export (Excel / PDF)
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
            if sonologist: qs = qs.filter(sonologist=sonologist)

        monthly_data = (
            qs.annotate(month=TruncMonth('date'))
              .values('month', 'sonologist')
              .annotate(
                  sonologist_name=F('sonologist__name'),
                  total_usg=Sum('total_ultra')
              )
              .order_by('month', 'sonologist')
        )

        headers = ['Month', 'Sonologist', 'Total USG']
        rows = [[r['month'].strftime("%B %Y"), r['sonologist_name'], r['total_usg']] for r in monthly_data]

        grand_total_usg = sum(r['total_usg'] for r in monthly_data)

        if fmt.lower() == 'xlsx':
            return export_to_excel(rows, headers, "monthly_report")
        elif fmt.lower() == 'pdf':
            return export_to_pdf(rows, headers, "monthly_report", extra_context={
                'grand_total_usg': grand_total_usg, 'group_by': 'monthly_sonologist'
            })
        return HttpResponse("Invalid format", status=400)
