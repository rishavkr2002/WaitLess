
from django.urls import path

from .views import (
    CallNextCustomerAPIView,
    CancelTokenAPIView,
    CompleteServiceAPIView,
    JoinQueueAPIView,
    QueueListAPIView,
    StartServiceAPIView,
    TokenStatusAPIView,
)

urlpatterns = [
    # List active queues
    path(
        "",
        QueueListAPIView.as_view(),
        name="queue-list",
    ),

    # Join a queue
    path(
        "join/",
        JoinQueueAPIView.as_view(),
        name="queue-join",
    ),

    # Check token status
    path(
        "tokens/<uuid:public_id>/",
        TokenStatusAPIView.as_view(),
        name="token-status",
    ),

    # Cancel a waiting token
    path(
        "tokens/<uuid:public_id>/cancel/",
        CancelTokenAPIView.as_view(),
        name="token-cancel",
    ),

    # Staff: call the next waiting customer
    path(
        "<int:queue_id>/call-next/",
        CallNextCustomerAPIView.as_view(),
        name="queue-call-next",
    ),

    # Staff: start service
    path(
        "tokens/<uuid:public_id>/start-service/",
        StartServiceAPIView.as_view(),
        name="token-start-service",
    ),

    # Staff: complete service
    path(
        "tokens/<uuid:public_id>/complete-service/",
        CompleteServiceAPIView.as_view(),
        name="token-complete-service",
    ),
]
