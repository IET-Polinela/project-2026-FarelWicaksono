from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import Report

# 1. Menampilkan daftar laporan (ListView)
class ReportListView(ListView):
    model = Report
    template_name = 'main_app/home.html'
    context_object_name = 'reports'
    ordering = ['-created_at']

# 2. Menampilkan detail laporan (DetailView)
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'
    context_object_name = 'report'

# 3. Membuat laporan baru (CreateView) - Ditambah Alert Feedback
class ReportCreateView(SuccessMessageMixin, CreateView):
    model = Report
    template_name = 'main_app/report_form.html'
    fields = ['title', 'category', 'description', 'location']
    success_url = reverse_lazy('home')
    success_message = "Laporan baru berhasil ditambahkan!"  # Poin 8

# 4. Mengedit laporan (UpdateView) - Ditambah Alert Feedback
class ReportUpdateView(SuccessMessageMixin, UpdateView):
    model = Report
    template_name = 'main_app/report_form.html'
    fields = ['title', 'category', 'description', 'location']
    success_url = reverse_lazy('home')
    success_message = "Data laporan berhasil diperbarui!"  # Poin 8

# 5. Menghapus laporan (DeleteView) - Ditambah Alert Feedback Manual
class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'main_app/report_confirm_delete.html'
    success_url = reverse_lazy('home')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Laporan berhasil dihapus!")  # Poin 8
        return super().delete(request, *args, **kwargs)

# 6. View Khusus Update Status Workflow - Ditambah Alert Feedback
class ReportUpdateStatusView(View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        current_status = report.status.upper() if report.status else ''
        
        if current_status == 'REPORTED' or current_status == 'Reported':
            report.status = 'VERIFIED'
            messages.success(request, "Status laporan berhasil diubah menjadi Verified!")  # Poin 8
        elif current_status == 'VERIFIED' or current_status == 'Verified':
            report.status = 'IN_PROGRESS'
            messages.success(request, "Status laporan berhasil diubah menjadi In Progress!")  # Poin 8
        elif current_status == 'IN_PROGRESS' or current_status == 'In Progress':
            report.status = 'RESOLVED'
            messages.success(request, "Status laporan berhasil diselesaikan (Resolved)!")  # Poin 8
            
        report.save()
        return redirect('report_detail', pk=report.id)