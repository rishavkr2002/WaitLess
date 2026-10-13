
from django.contrib import admin
from django.urls import include, path

from config.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("api/health/", home, name="health"),
    path("api/", include("organizations.urls")),
]
