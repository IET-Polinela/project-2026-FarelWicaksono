from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    """Serializer laporan untuk SPA Citizen Lab Session 12."""

    reporter = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id',
            'title',
            'category',
            'description',
            'location',
            'status',
            'reporter',
            'is_owner',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'reporter',
            'is_owner',
            'created_at',
            'updated_at',
        ]

    def get_reporter(self, obj):
        """
        Feed Kota tidak pernah mengirim username asli ke client. Penyensoran
        dilakukan pada serializer agar identitas tidak bocor melalui Network.
        """
        request = self.context.get('request')
        tab = request.query_params.get('tab') if request else None
        if tab == 'feed':
            return 'Warga Anonim'
        return obj.reporter.username if obj.reporter else 'Warga Anonim'

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and obj.reporter_id == request.user.id
        )

    def validate_status(self, value):
        """Citizen hanya boleh menyimpan DRAFT atau mengajukannya sebagai REPORTED."""
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        is_admin = bool(
            user
            and user.is_authenticated
            and (getattr(user, 'is_admin', False) or getattr(user, 'is_superuser', False))
        )
        if not is_admin and value not in {'DRAFT', 'REPORTED'}:
            raise serializers.ValidationError(
                'Citizen hanya dapat memilih status DRAFT atau REPORTED.'
            )
        return value
