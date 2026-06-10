from django.urls import path
from .views import (
    ReportListView, ReportDetailView, ReportCreateView, 
    ReportUpdateView, ReportDeleteView, ReportUpdateStatusView
)

urlpatterns = [
    # Jalur halaman utama
    path('', ReportListView.as_view(), name='home'),
    
    # Jalur menu /reports/ di navbar agar tampilannya tetap menggunakan ListView yang rapi
    path('reports/', ReportListView.as_view(), name='reports_list'),
    
    # Operasi CRUD data laporan
    path('report/add/', ReportCreateView.as_view(), name='add_report'),
    path('report/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),
    path('report/<int:pk>/edit/', ReportUpdateView.as_view(), name='report_edit'),
    path('report/<int:pk>/delete/', ReportDeleteView.as_view(), name='report_delete'),
    path('report/<int:pk>/update-status/', ReportUpdateStatusView.as_view(), name='update_status'),
]