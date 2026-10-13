
from django.contrib import admin
from .models import Queue, Token


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "service", "is_active", "created_at")
    search_fields = ("name", "service__name")
    list_filter = ("is_active",)
    list_per_page = 20


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "token_number",
        "customer_name",
        "queue",
        "status",
        "joined_at",
    )
    search_fields = ("customer_name",)
    list_filter = ("status", "queue")
    list_per_page = 20
    readonly_fields = ("joined_at",)
