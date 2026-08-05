from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions

from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """Endpoint registrasi akun Citizen baru."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(exclude=True)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)