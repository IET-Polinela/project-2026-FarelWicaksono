from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count
from main_app.models import Report

class DashboardMainView(TemplateView):
    template_name = 'dashboard/index.html'

def dashboard_api_data(request):
    status_data = Report.objects.values('status').annotate(total=Count('status'))
    category_data = Report.objects.values('category').annotate(total=Count('category'))
    
    # Mengambil 5 data terbaru memakai order_by bawaan Django yang aman
    recent_reported = list(Report.objects.filter(status='REPORTED').order_by('-id')[:5].values('id', 'title', 'category', 'location'))
    recent_resolved = list(Report.objects.filter(status='RESOLVED').order_by('-id')[:5].values('id', 'title', 'category', 'location'))

    response_payload = {
        'status_stats': {item['status']: item['total'] for item in status_data},
        'category_stats': {item['category']: item['total'] for item in category_data},
        'recent_reported': recent_reported,
        'recent_resolved': recent_resolved,
    }
    
    return JsonResponse(response_payload)