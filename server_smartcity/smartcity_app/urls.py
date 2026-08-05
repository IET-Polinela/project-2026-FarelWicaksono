from django.contrib import admin
from django.urls import include, path

from django_scalar.views import scalar_viewer
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from main_app.api_views import ReportViewSet
from usermanagement_24782049.api_views import RegisterView


# ============================================================
# API ROUTER
# ============================================================

router = DefaultRouter()

# Endpoint lama dipertahankan agar frontend sebelumnya
# tetap dapat menggunakan /api/reports/.
router.register(
    r"reports",
    ReportViewSet,
    basename="reports-api",
)

# Endpoint tambahan untuk mengikuti skenario Lab Session 14:
# POST /api/report/
# GET  /api/report/
router.register(
    r"report",
    ReportViewSet,
    basename="report-api",
)


# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [
    # Django Admin
    path(
        "admin/",
        admin.site.urls,
    ),

    # ========================================================
    # OPENAPI DOCUMENTATION - LAB SESSION 14
    # ========================================================

    # Schema mentah OpenAPI dalam format YAML/JSON.
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    # Swagger UI untuk menguji endpoint secara interaktif.
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
        ),
        name="swagger-ui",
    ),

    # Scalar UI untuk dokumentasi dan code generation.
    path(
        "api/docs/scalar/",
        scalar_viewer,
        name="scalar-ui",
    ),

    # ========================================================
    # AUTHENTICATION API
    # ========================================================

    # Registrasi akun Citizen.
    path(
        "api/register/",
        RegisterView.as_view(),
        name="api-register",
    ),

    # Login JWT untuk memperoleh access dan refresh token.
    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),

    # Memperbarui JWT access token.
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),

    # ========================================================
    # REPORT API
    # ========================================================

    path(
        "api/",
        include(router.urls),
    ),

    # ========================================================
    # URL DARI LAB SEBELUMNYA
    # ========================================================

    path(
        "auth/",
        include("usermanagement_24782049.urls"),
    ),

    path(
        "about/",
        include("about.urls"),
    ),

    path(
        "contacts/",
        include("contacts.urls"),
    ),

    path(
        "dashboard/",
        include("dashboard_24782049.urls"),
    ),

    # Diletakkan terakhir agar tidak menutupi route lain.
    path(
        "",
        include("main_app.urls"),
    ),
]