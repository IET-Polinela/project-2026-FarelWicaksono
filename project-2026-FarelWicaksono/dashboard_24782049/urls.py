from django.urls import path
from .views import DashboardMainView, dashboard_api_data

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardMainView.as_view(), name='index'),
    path('api/data/', dashboard_api_data, name='api_data'),
]