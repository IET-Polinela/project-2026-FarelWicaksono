from rest_framework import permissions


class IsCitizen(permissions.BasePermission):
    """Mengizinkan pembuatan laporan hanya untuk akun Citizen/member."""

    message = 'Hanya Citizen yang dapat membuat laporan.'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, 'is_member', False)
            and not getattr(user, 'is_admin', False)
            and not getattr(user, 'is_staff', False)
            and not getattr(user, 'is_superuser', False)
        )


class IsOwnerAndDraftOrReadOnly(permissions.BasePermission):
    """
    Akses baca diperbolehkan. Update dan delete hanya boleh dilakukan oleh
    pemilik laporan ketika status laporan masih DRAFT.
    """

    message = 'Laporan hanya dapat diubah atau dihapus oleh pemilik saat status masih DRAFT.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.reporter == request.user and obj.status == 'DRAFT'
