
from django.urls import path

from .views import (
    CallNextCustomerAPIView,
    CancelTokenAPIView,
    CompleteServiceAPIView,
    JoinQueueAPIView,
    QueueCustomerListAPIView,
    QueueDashboardAPIView,
    QueueListAPIView,
    StartServiceAPIView,
    TokenStatusAPIView,
)

urlpatterns = [
    path("", QueueListAPIView.as_view(), name="queue-list"),
    path("join/", JoinQueueAPIView.as_view(), name="queue-join"),

    path(
        "dashboard/<int:queue_id>/",
        QueueDashboardAPIView.as_view(),
        name="queue-dashboard",
    ),
    path(
        "<int:queue_id>/customers/",
        QueueCustomerListAPIView.as_view(),
        name="queue-customers",
    ),

    path(
        "tokens/<uuid:public_id>/",
        TokenStatusAPIView.as_view(),
        name="token-status",
    ),
    path(
        "tokens/<uuid:public_id>/cancel/",
        CancelTokenAPIView.as_view(),
        name="token-cancel",
    ),
    path(
        "<int:queue_id>/call-next/",
        CallNextCustomerAPIView.as_view(),
        name="queue-call-next",
    ),
    path(
        "tokens/<uuid:public_id>/start-service/",
        StartServiceAPIView.as_view(),
        name="token-start-service",
    ),
    path(
        "tokens/<uuid:public_id>/complete-service/",
        CompleteServiceAPIView.as_view(),
        name="token-complete-service",
    ),
]
