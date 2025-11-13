from django.urls import path
from .views import (
    HomeView,
    DashboardPageView,
    DashboardDataView,
    ReportListView,
    DailyReportView,
    MonthlyReportView,
    ExportView,
    DailyReportExportView,
    MonthlyReportExportView,
)

app_name = "reports"

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardPageView.as_view(), name='dashboard'),
    path('dashboard/data/', DashboardDataView.as_view(), name='dashboard-data'),
    path('reports/', ReportListView.as_view(), name='report_list'),
    path('reports/daily/', DailyReportView.as_view(), name='daily_report'),
    path('reports/daily/export/<str:fmt>/', DailyReportExportView.as_view(), name='daily_export'),
    path('reports/monthly/', MonthlyReportView.as_view(), name='monthly_report'),
    path('reports/monthly/export/<str:fmt>/', MonthlyReportExportView.as_view(), name='monthly_export'),
    path('export/<str:fmt>/', ExportView.as_view(), name='export'),

]
