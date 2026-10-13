
from rest_framework import serializers
from .models import Organization, Service


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "description",
            "address",
            "phone",
            "email",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "organization",
            "name",
            "description",
            "average_service_time",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
