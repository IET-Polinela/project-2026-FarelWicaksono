from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'reporter', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'category', 'location', 'reporter__username')
    readonly_fields = ('created_at',)
