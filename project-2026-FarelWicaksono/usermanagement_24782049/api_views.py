from rest_framework import generics, permissions

from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """Endpoint registrasi akun Citizen baru."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
