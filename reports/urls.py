from django.urls import path
from .views import HomeView, ReportListView, ExportView

app_name = "reports"   # ✅ Add this line

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('reports/', ReportListView.as_view(), name='report_list'),
    path('export/<str:fmt>/', ExportView.as_view(), name='export'), 
]
