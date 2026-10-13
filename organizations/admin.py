
from django.contrib import admin
from .models import Organization, Service


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "email", "is_active")
    search_fields = ("name", "address", "email")
    list_filter = ("is_active",)
    list_per_page = 20


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "organization",
        "average_service_time",
        "is_active",
    )
    search_fields = ("name", "organization__name")
    list_filter = ("is_active", "organization")
    list_per_page = 20
