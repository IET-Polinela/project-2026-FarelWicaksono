from django.db.models import Q
from rest_framework import permissions, viewsets

from .models import Report
from .permissions import IsCitizen, IsOwnerAndDraftOrReadOnly
from .serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    """CRUD API Report dengan autentikasi JWT dan permission berbasis objek."""

    serializer_class = ReportSerializer

    def get_queryset(self):
        """
        Admin dapat melihat seluruh laporan. Citizen melihat seluruh laporan
        non-DRAFT dan hanya DRAFT miliknya sendiri.
        """
        user = self.request.user
        queryset = Report.objects.select_related('reporter').all()

        if not user.is_authenticated:
            return Report.objects.none()

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
        # Identitas pelapor tidak dipercaya dari payload klien. Pelapor diambil
        # dari user yang telah divalidasi oleh JWTAuthentication.
        serializer.save(reporter=self.request.user, status='DRAFT')
