from django.db.models import Q
from rest_framework import pagination, permissions, viewsets

from .models import Report
from .permissions import IsCitizen, IsOwnerAndDraftOrReadOnly
from .serializers import ReportSerializer


# ============================================================
# PAGINATION
# ============================================================

class ReportPagination(pagination.PageNumberPagination):
    """
    Pagination server-side:
    10 item per halaman, dapat dibesarkan untuk rekap.
    """

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


# ============================================================
# REPORT API VIEWSET
# ============================================================

class ReportViewSet(viewsets.ModelViewSet):
    """
    CRUD API Report dengan JWT, filtering tab,
    sorting, pagination, dan proteksi privasi DRAFT.
    """

    serializer_class = ReportSerializer
    pagination_class = ReportPagination

    # --------------------------------------------------------
    # QUERYSET / VISIBILITY
    # --------------------------------------------------------

    def get_queryset(self):
        user = self.request.user

        # User belum login tidak mendapatkan data apa pun.
        if not user.is_authenticated:
            return Report.objects.none()

        queryset = (
            Report.objects
            .select_related('reporter')
            .order_by('-updated_at', '-id')
        )

        tab = self.request.query_params.get('tab')

        # ====================================================
        # TAB: LAPORAN SAYA
        # ====================================================
        # Citizen boleh melihat seluruh laporannya sendiri,
        # termasuk laporan yang masih DRAFT.
        if tab == 'my_reports':
            return queryset.filter(reporter=user)

        # ====================================================
        # TAB: FEED KOTA
        # ====================================================
        # Feed Kota:
        # - tidak menampilkan laporan sendiri
        # - tidak pernah menampilkan DRAFT
        if tab == 'feed':
            return (
                queryset
                .exclude(reporter=user)
                .exclude(status='DRAFT')
            )

        # ====================================================
        # ADMIN
        # ====================================================
        # Admin hanya boleh melihat laporan Citizen setelah
        # laporan tersebut diajukan.
        #
        # Citizen + DRAFT       -> HIDDEN
        # Citizen + REPORTED    -> VISIBLE
        # Citizen + VERIFIED    -> VISIBLE
        # Citizen + IN_PROGRESS -> VISIBLE
        # Citizen + RESOLVED    -> VISIBLE
        #
        # DRAFT reporter=NULL tetap dipertahankan untuk
        # kompatibilitas data lama/lab sebelumnya.
        is_admin_user = bool(
            getattr(user, 'is_admin', False)
            or getattr(user, 'is_staff', False)
            or getattr(user, 'is_superuser', False)
        )

        if is_admin_user:
            return queryset.exclude(
                status='DRAFT',
                reporter__isnull=False
            )

        # ====================================================
        # CITIZEN - ENDPOINT TANPA PARAMETER
        # ====================================================
        # Citizen dapat melihat:
        # - semua laporan non-DRAFT
        # - DRAFT miliknya sendiri
        #
        # Citizen tidak dapat melihat DRAFT milik orang lain.
        return queryset.filter(
            ~Q(status='DRAFT')
            | Q(
                status='DRAFT',
                reporter=user
            )
        )

    # --------------------------------------------------------
    # PERMISSIONS
    # --------------------------------------------------------

    def get_permissions(self):

        # Create laporan hanya Citizen yang sudah login.
        if self.action == 'create':
            permission_classes = [
                permissions.IsAuthenticated,
                IsCitizen,
            ]

        # Update / delete harus melewati proteksi:
        # hanya pemilik dan hanya ketika masih DRAFT.
        elif self.action in [
            'update',
            'partial_update',
            'destroy',
        ]:
            permission_classes = [
                permissions.IsAuthenticated,
                IsOwnerAndDraftOrReadOnly,
            ]

        # GET list/detail hanya membutuhkan autentikasi.
        else:
            permission_classes = [
                permissions.IsAuthenticated,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    def perform_create(self, serializer):
        """
        Reporter tidak boleh berasal dari payload frontend.
        Reporter selalu diambil dari user JWT yang login.

        Citizen dapat:
        - Simpan DRAFT
        - Ajukan sebagai REPORTED
        """

        requested_status = serializer.validated_data.get(
            'status',
            'DRAFT'
        )

        serializer.save(
            reporter=self.request.user,
            status=requested_status
        )