from django.db.models import Q
from rest_framework import pagination, permissions, viewsets

from .models import Report
from .permissions import IsCitizen, IsOwnerAndDraftOrReadOnly
from .serializers import ReportSerializer


class ReportPagination(pagination.PageNumberPagination):
    """Pagination server-side: 10 item per halaman, dapat dibesarkan untuk rekap."""

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ReportViewSet(viewsets.ModelViewSet):
    """CRUD API Report dengan JWT, filtering tab, sorting, dan pagination."""

    serializer_class = ReportSerializer
    pagination_class = ReportPagination

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Report.objects.none()

        queryset = Report.objects.select_related('reporter').order_by('-updated_at', '-id')
        tab = self.request.query_params.get('tab')

        # Tab Laporan Saya: seluruh laporan milik user, termasuk DRAFT.
        if tab == 'my_reports':
            return queryset.filter(reporter=user)

        # Tab Feed Kota: hanya laporan warga lain yang sudah diajukan/non-DRAFT.
        if tab == 'feed':
            return queryset.exclude(reporter=user).exclude(status='DRAFT')

        # Endpoint tanpa parameter tetap mempertahankan aturan visibilitas Lab 10.
        if getattr(user, 'is_admin', False) or getattr(user, 'is_superuser', False):
            return queryset

        return queryset.filter(
            ~Q(status='DRAFT') | Q(status='DRAFT', reporter=user)
        )

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsCitizen]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [
                permissions.IsAuthenticated,
                IsOwnerAndDraftOrReadOnly,
            ]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Reporter selalu berasal dari JWT, bukan dari payload yang dapat dimanipulasi.
        requested_status = serializer.validated_data.get('status', 'DRAFT')
        serializer.save(reporter=self.request.user, status=requested_status)
