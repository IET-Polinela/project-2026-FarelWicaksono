from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    """Serializer Report untuk endpoint REST Lab Session 10."""

    reporter = serializers.SerializerMethodField()

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
            'created_at',
        ]
        read_only_fields = ['id', 'status', 'reporter', 'created_at']

    def get_reporter(self, obj):
        return obj.reporter.username if obj.reporter else None
