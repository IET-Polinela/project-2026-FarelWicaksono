from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q
from .models import Report

# Helper kecil agar label & warna badge status konsisten antara halaman utama dan respons JSON
STATUS_LABELS = {
    'REPORTED': 'Reported',
    'VERIFIED': 'Verified',
    'IN_PROGRESS': 'In Progress',
    'RESOLVED': 'Resolved',
}
STATUS_BADGE_CLASS = {
    'REPORTED': 'bg-warning text-dark',
    'VERIFIED': 'bg-info text-dark',
    'IN_PROGRESS': 'bg-primary',
    'RESOLVED': 'bg-success',
}

def _serialize_report(report):
    status_key = (report.status or '').upper().replace(' ', '_')
    return {
        'id': report.id,
        'title': report.title,
        'category': report.category,
        'location': report.location,
        'description': report.description,
        'status': report.status,
        'status_label': STATUS_LABELS.get(status_key, report.status),
        'status_badge_class': STATUS_BADGE_CLASS.get(status_key, 'bg-secondary'),
        'created_at': report.created_at.strftime('%d %b %Y, %H:%M'),
    }

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


# 7. API Live Search - Mengembalikan daftar laporan dalam format JSON (untuk fetch() tanpa reload)
def report_search_api(request):
    query = request.GET.get('q', '').strip()
    reports = Report.objects.all().order_by('-created_at')

    if query:
        reports = reports.filter(
            Q(title__icontains=query) |
            Q(category__icontains=query) |
            Q(location__icontains=query)
        )

    # Batasi hasil agar payload tetap ringan, selaras dengan prinsip efisiensi fetch
    reports = reports[:50]
    data = {
        'count': len(reports),
        'results': [_serialize_report(r) for r in reports],
    }
    return JsonResponse(data)


# 8. API Detail Modal - Mengembalikan satu laporan dalam format JSON (untuk modal pop-up)
def report_detail_api(request, pk):
    report = get_object_or_404(Report, pk=pk)
    return JsonResponse(_serialize_report(report))