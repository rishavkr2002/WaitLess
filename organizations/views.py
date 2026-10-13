
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Organization, Service
from .serializers import OrganizationSerializer, ServiceSerializer


class OrganizationListAPIView(generics.ListAPIView):
    queryset = Organization.objects.filter(is_active=True)
    serializer_class = OrganizationSerializer
    permission_classes = [AllowAny]


class ServiceListAPIView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Service.objects.filter(
            is_active=True,
            organization__is_active=True,
        )

        organization_id = self.request.query_params.get("organization")

        if organization_id:
            queryset = queryset.filter(
                organization_id=organization_id
            )

        return queryset
