from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from main_app.api_views import ReportViewSet
from usermanagement_24782049.api_views import RegisterView


router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report-api')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Endpoint Lab Session 10: registrasi, login JWT, dan refresh token.
    path('api/register/', RegisterView.as_view(), name='api-register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/', include(router.urls)),

    # Endpoint dan halaman dari Lab sebelumnya tetap dipertahankan.
    path('auth/', include('usermanagement_24782049.urls')),
    path('', include('main_app.urls')),
    path('about/', include('about.urls')),
    path('contacts/', include('contacts.urls')),
    path('dashboard/', include('dashboard_24782049.urls')),
]
