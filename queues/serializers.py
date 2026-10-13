
from rest_framework import serializers
from .models import Queue, Token


class QueueSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(
        source="service.name",
        read_only=True,
    )
    organization_name = serializers.CharField(
        source="service.organization.name",
        read_only=True,
    )

    class Meta:
        model = Queue
        fields = [
            "id",
            "name",
            "service",
            "service_name",
            "organization_name",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TokenSerializer(serializers.ModelSerializer):
    queue_name = serializers.CharField(
        source="queue.name",
        read_only=True,
    )

    class Meta:
        model = Token
        fields = [
            "id",
            "queue",
            "queue_name",
            "token_number",
            "customer_name",
            "status",
            "joined_at",
        ]
        read_only_fields = [
            "id",
            "token_number",
            "status",
            "joined_at",
        ]
