from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    """Serializer laporan untuk SPA Citizen dan automated test Lab 15."""

    reporter = serializers.SerializerMethodField()
    reporter_name = serializers.SerializerMethodField()
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
            'reporter_name',
            'is_owner',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'reporter',
            'reporter_name',
            'is_owner',
            'created_at',
            'updated_at',
        ]

    def _visible_reporter_name(self, obj):
        request = self.context.get('request')
        if request is None:
            return 'Warga Anonim'

        tab = request.query_params.get('tab')
        if tab == 'feed':
            return 'Warga Anonim'

        user = getattr(request, 'user', None)
        is_authenticated = bool(user and user.is_authenticated)
        is_owner = bool(is_authenticated and obj.reporter_id == user.id)
        is_admin = bool(
            is_authenticated
            and (
                getattr(user, 'is_admin', False)
                or getattr(user, 'is_staff', False)
                or getattr(user, 'is_superuser', False)
            )
        )

        if (is_owner or is_admin) and obj.reporter:
            return obj.reporter.username

        return 'Warga Anonim'

    def get_reporter(self, obj):
        return self._visible_reporter_name(obj)

    def get_reporter_name(self, obj):
        return self._visible_reporter_name(obj)

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and obj.reporter_id == request.user.id
        )

    def validate_status(self, value):
        """Citizen hanya boleh menyimpan DRAFT atau REPORTED."""
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        is_admin = bool(
            user
            and user.is_authenticated
            and (
                getattr(user, 'is_admin', False)
                or getattr(user, 'is_staff', False)
                or getattr(user, 'is_superuser', False)
            )
        )

        if not is_admin and value not in {'DRAFT', 'REPORTED'}:
            raise serializers.ValidationError(
                'Citizen hanya dapat memilih status DRAFT atau REPORTED.'
            )

        return value
