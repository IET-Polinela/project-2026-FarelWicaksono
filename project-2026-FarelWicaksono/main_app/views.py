from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Report

# 1. Menampilkan daftar laporan (ListView) [cite: 40]
class ReportListView(ListView):
    model = Report
    template_name = 'main_app/home.html'
    context_object_name = 'reports'
    ordering = ['-created_at']

# 2. Menampilkan detail laporan (DetailView) [cite: 41]
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'
    context_object_name = 'report'

# 3. Membuat laporan baru (CreateView) [cite: 42]
class ReportCreateView(CreateView):
    model = Report
    template_name = 'main_app/add_report.html'
    # Field 'status' tidak disertakan agar otomatis menggunakan default 'REPORTED' [cite: 35]
    fields = ['title', 'category', 'description', 'location']
    success_url = reverse_lazy('home')

# 4. Mengedit laporan (UpdateView) [cite: 43]
class ReportUpdateView(UpdateView):
    model = Report
    template_name = 'main_app/add_report.html'
    # Sesuai modul, status tidak diubah melalui menu edit biasa [cite: 48]
    fields = ['title', 'category', 'description', 'location']
    success_url = reverse_lazy('home')

# 5. Menghapus laporan (DeleteView) [cite: 44]
class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'main_app/report_confirm_delete.html'
    success_url = reverse_lazy('home')

# 6. View Khusus Update Status Workflow [cite: 47, 52]
class ReportUpdateStatusView(View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')
        
        # Validasi sederhana sebelum menyimpan ke database [cite: 73]
        if new_status:
            report.status = new_status
            report.save()
            
        return redirect('home')