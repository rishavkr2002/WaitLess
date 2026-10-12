from django.contrib import admin
from .models import Organization, Service, Queue, QueueTicket


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "owner__username",
    )

    list_filter = ("is_active",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "organization",
        "average_service_time",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "organization",
    )

    search_fields = (
        "name",
        "organization__name",
    )


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "service",
        "current_number",
        "last_ticket_number",
        "is_active",
        "created_at",
    )

    list_filter = ("is_active",)

    search_fields = (
        "name",
        "service__name",
    )


@admin.register(QueueTicket)
class QueueTicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_number",
        "customer",
        "queue",
        "status",
        "position",
        "estimated_wait_time",
        "joined_at",
    )

    list_filter = (
        "status",
        "queue",
    )

    search_fields = (
        "customer__username",
        "customer__email",
    )

    ordering = ("-joined_at",)
