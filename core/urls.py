"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from drf_spectacular.utils import extend_schema


class HiddenSpectacularAPIView(SpectacularAPIView):
    """
    Custom SpectacularAPIView that is excluded from the generated schema.
    This prevents the '/api/schema/' endpoint from appearing in the API documentation.
    """

    @extend_schema(exclude=True)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/accounts/", include("accounts.ap1.v1.urls")),
    # OpenAPI schema (excluded from documentation)
    path("api/schema/", HiddenSpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    # ReDoc
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
