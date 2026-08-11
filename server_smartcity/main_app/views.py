from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q

from rest_framework.decorators import api_view

from .models import Report


# ============================================================
# HELPER STATUS
# ============================================================

STATUS_LABELS = {
    'DRAFT': 'Draft',
    'REPORTED': 'Reported',
    'VERIFIED': 'Verified',
    'IN_PROGRESS': 'In Progress',
    'RESOLVED': 'Resolved',
}

STATUS_BADGE_CLASS = {
    'DRAFT': 'bg-secondary',
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
        'status_label': STATUS_LABELS.get(
            status_key,
            report.status
        ),
        'status_badge_class': STATUS_BADGE_CLASS.get(
            status_key,
            'bg-secondary'
        ),
        'created_at': report.created_at.strftime(
            '%d %b %Y, %H:%M'
        ),
    }


# ============================================================
# PRIVACY DRAFT CITIZEN
# ============================================================

def _visible_reports_for_admin():
    """
    DRAFT milik Citizen bersifat privat.

    Report yang dibuat Citizen melalui API mempunyai reporter.
    Karena itu:
        Citizen + DRAFT  -> disembunyikan dari Admin
        Citizen + REPORTED/VERIFIED/... -> terlihat Admin

    DRAFT dengan reporter NULL tetap ditampilkan untuk
    kompatibilitas data lama atau report yang dibuat Admin.
    """

    return Report.objects.exclude(
        status='DRAFT',
        reporter__isnull=False
    )


# ============================================================
# 1. DAFTAR LAPORAN
# ============================================================

class ReportListView(ListView):
    model = Report
    template_name = 'main_app/home.html'
    context_object_name = 'reports'

    def get_queryset(self):
        return _visible_reports_for_admin().order_by(
            '-created_at'
        )


# ============================================================
# 2. DETAIL LAPORAN
# ============================================================

class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'
    context_object_name = 'report'

    def get_queryset(self):
        # Citizen DRAFT tidak boleh dapat dibuka dengan URL manual.
        return _visible_reports_for_admin()


# ============================================================
# 3. CREATE LAPORAN - ADMIN
# ============================================================

class ReportCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    CreateView
):
    model = Report
    template_name = 'main_app/report_form.html'

    fields = [
        'title',
        'category',
        'description',
        'location',
    ]

    success_url = reverse_lazy('home')
    success_message = (
        "Laporan baru berhasil ditambahkan!"
    )

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('login')

        if not request.user.is_admin:
            messages.error(
                request,
                "🔒 Akses Ditolak! "
                "Fitur ini hanya dapat dieksekusi "
                "oleh Admin Otoritas."
            )
            return redirect('home')

        return super().dispatch(
            request,
            *args,
            **kwargs
        )


# ============================================================
# 4. EDIT LAPORAN - ADMIN
# ============================================================

class ReportUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    UpdateView
):
    model = Report
    template_name = 'main_app/report_form.html'

    fields = [
        'title',
        'category',
        'description',
        'location',
    ]

    success_url = reverse_lazy('home')

    success_message = (
        "Data laporan berhasil diperbarui!"
    )

    def get_queryset(self):
        # Admin tidak boleh mengedit DRAFT milik Citizen.
        return _visible_reports_for_admin()

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('login')

        if not request.user.is_admin:
            messages.error(
                request,
                "🔒 Akses Ditolak! "
                "Fitur ini hanya dapat dieksekusi "
                "oleh Admin Otoritas."
            )
            return redirect('home')

        return super().dispatch(
            request,
            *args,
            **kwargs
        )


# ============================================================
# 5. DELETE LAPORAN - ADMIN
# ============================================================

class ReportDeleteView(
    LoginRequiredMixin,
    DeleteView
):
    model = Report

    template_name = (
        'main_app/report_confirm_delete.html'
    )

    success_url = reverse_lazy('home')

    def get_queryset(self):
        # Admin tidak boleh menghapus DRAFT milik Citizen.
        return _visible_reports_for_admin()

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('login')

        if not request.user.is_admin:
            messages.error(
                request,
                "🔒 Akses Ditolak! "
                "Fitur ini hanya dapat dieksekusi "
                "oleh Admin Otoritas."
            )
            return redirect('home')

        return super().dispatch(
            request,
            *args,
            **kwargs
        )

    def delete(
        self,
        request,
        *args,
        **kwargs
    ):

        messages.success(
            request,
            "Laporan berhasil dihapus!"
        )

        return super().delete(
            request,
            *args,
            **kwargs
        )


# ============================================================
# 6. UPDATE STATUS WORKFLOW - ADMIN
# ============================================================

class ReportUpdateStatusView(
    LoginRequiredMixin,
    View
):

    def dispatch(
        self,
        request,
        *args,
        **kwargs
    ):

        if not request.user.is_authenticated:
            return redirect('login')

        if not request.user.is_admin:
            messages.error(
                request,
                "🔒 Akses Ditolak! "
                "Fitur ini hanya dapat dieksekusi "
                "oleh Admin Otoritas."
            )
            return redirect('home')

        return super().dispatch(
            request,
            *args,
            **kwargs
        )

    def post(self, request, pk):

        # Citizen DRAFT tidak boleh diproses Admin.
        report = get_object_or_404(
            _visible_reports_for_admin(),
            pk=pk
        )

        current_status = (
            report.status.upper()
            if report.status
            else ''
        )

        if current_status == 'REPORTED':

            report.status = 'VERIFIED'

            messages.success(
                request,
                "Status laporan berhasil diubah "
                "menjadi Verified!"
            )

        elif current_status == 'VERIFIED':

            report.status = 'IN_PROGRESS'

            messages.success(
                request,
                "Status laporan berhasil diubah "
                "menjadi In Progress!"
            )

        elif current_status == 'IN_PROGRESS':

            report.status = 'RESOLVED'

            messages.success(
                request,
                "Status laporan berhasil "
                "diselesaikan (Resolved)!"
            )

        elif current_status == 'RESOLVED':

            messages.info(
                request,
                "Laporan sudah berstatus Resolved."
            )

            return redirect(
                'report_detail',
                pk=report.id
            )

        else:

            messages.warning(
                request,
                "Status laporan tidak dapat "
                "diproses oleh Admin."
            )

            return redirect('home')

        report.save()

        return redirect(
            'report_detail',
            pk=report.id
        )


# ============================================================
# 7. LIVE SEARCH ADMIN
# ============================================================

@api_view(['GET'])
def report_search_api(request):
    """
    Live search khusus Admin.

    Citizen DRAFT tidak boleh ikut dikirim
    pada response JSON.
    """

    user = request.user

    if not user or not user.is_authenticated:

        return JsonResponse(
            {
                'detail':
                'Authentication credentials '
                'were not provided.'
            },
            status=401,
        )

    is_admin_user = bool(
        getattr(user, 'is_admin', False)
        or getattr(user, 'is_staff', False)
        or getattr(user, 'is_superuser', False)
    )

    if not is_admin_user:

        return JsonResponse(
            {
                'detail':
                'Akses pencarian laporan '
                'hanya untuk Admin.'
            },
            status=403,
        )

    query = request.GET.get(
        'q',
        ''
    ).strip()

    reports = (
        _visible_reports_for_admin()
        .order_by('-created_at')
    )

    if query:

        reports = reports.filter(
            Q(title__icontains=query)
            | Q(category__icontains=query)
            | Q(location__icontains=query)
        )

    reports = reports[:50]

    data = {
        'count': len(reports),

        'results': [
            _serialize_report(report)
            for report in reports
        ],
    }

    return JsonResponse(data)


# ============================================================
# LIVE SEARCH KHUSUS PLAYWRIGHT LAB 15
# ============================================================

def report_search_playwright(request):

    user = request.user

    if not user or not user.is_authenticated:

        return JsonResponse(
            {
                'detail':
                'Authentication credentials '
                'were not provided.'
            },
            status=401,
        )

    is_admin = bool(
        getattr(user, 'is_admin', False)
        or getattr(user, 'is_staff', False)
        or getattr(user, 'is_superuser', False)
    )

    if not is_admin:

        return JsonResponse(
            {
                'detail':
                'Akses pencarian laporan '
                'hanya untuk Admin.'
            },
            status=403,
        )

    query = request.GET.get(
        'q',
        ''
    ).strip()

    reports = (
        _visible_reports_for_admin()
        .order_by('-created_at')
    )

    if query:

        reports = reports.filter(
            Q(title__icontains=query)
            | Q(category__icontains=query)
            | Q(location__icontains=query)
        )

    reports = list(
        reports[:50]
    )

    return JsonResponse(
        {
            'count': len(reports),

            'results': [
                _serialize_report(report)
                for report in reports
            ],
        }
    )


# ============================================================
# 8. API DETAIL MODAL ADMIN
# ============================================================

def report_detail_api(request, pk):

    # Citizen DRAFT tidak boleh bocor lewat modal/API.
    report = get_object_or_404(
        _visible_reports_for_admin(),
        pk=pk
    )

    return JsonResponse(
        _serialize_report(report)
    )