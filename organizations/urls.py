
from django.urls import path
from .views import OrganizationListAPIView, ServiceListAPIView

urlpatterns = [
    path(
        "organizations/",
        OrganizationListAPIView.as_view(),
        name="organization-list",
    ),
    path(
        "services/",
        ServiceListAPIView.as_view(),
        name="service-list",
    ),
]
