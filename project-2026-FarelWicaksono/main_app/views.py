from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Report

# 1. Menampilkan daftar laporan (ListView) - Terbuka untuk umum/Citizen
class ReportListView(ListView):
    model = Report
    template_name = 'main_app/home.html'
    context_object_name = 'reports'
    ordering = ['-created_at']

# 2. Menampilkan detail laporan (DetailView) - Terbuka untuk umum/Citizen
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'
    context_object_name = 'report'

# 3. Membuat laporan baru (CreateView) - Proteksi Admin Eksklusif
class ReportCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Report
    template_name = 'main_app/report_form.html'
    fields = ['title', 'category', 'description', 'location']
    success_url = reverse_lazy('home')
    success_message = "Laporan baru berhasil ditambahkan!"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, "🔒 Akses Ditolak! Fitur ini hanya dapat dieksekusi oleh Admin Otoritas.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

# 4. Mengedit laporan (UpdateView) - Proteksi Admin Eksklusif
class ReportUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Report
    template_name = 'main_app/report_form.html'
    fields = ['title', 'category', 'description', 'location']
    success_url = reverse_lazy('home')
    success_message = "Data laporan berhasil diperbarui!"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, "🔒 Akses Ditolak! Fitur ini hanya dapat dieksekusi oleh Admin Otoritas.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

# 5. Menghapus laporan (DeleteView) - Proteksi Admin Eksklusif
class ReportDeleteView(LoginRequiredMixin, DeleteView):
    model = Report
    template_name = 'main_app/report_confirm_delete.html'
    success_url = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, "🔒 Akses Ditolak! Fitur ini hanya dapat dieksekusi oleh Admin Otoritas.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Laporan berhasil dihapus!")
        return super().delete(request, *args, **kwargs)

# 6. View Khusus Update Status Workflow - Proteksi Admin Eksklusif
class ReportUpdateStatusView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, "🔒 Akses Ditolak! Fitur ini hanya dapat dieksekusi oleh Admin Otoritas.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        current_status = report.status.upper() if report.status else ''
        
        if current_status in ['REPORTED', 'Reported']:
            report.status = 'VERIFIED'
            messages.success(request, "Status laporan berhasil diubah menjadi Verified!")
        elif current_status in ['VERIFIED', 'Verified']:
            report.status = 'IN_PROGRESS'
            messages.success(request, "Status laporan berhasil diubah menjadi In Progress!")
        elif current_status in ['IN_PROGRESS', 'In Progress']:
            report.status = 'RESOLVED'
            messages.success(request, "Status laporan berhasil diselesaikan (Resolved)!")
            
        report.save()
        return redirect('report_detail', pk=report.id)