
from django.urls import path

from .views import (
    CancelTokenAPIView,
    JoinQueueAPIView,
    QueueListAPIView,
    TokenStatusAPIView,
)

urlpatterns = [
    # List all active queues
    path(
        "",
        QueueListAPIView.as_view(),
        name="queue-list",
    ),

    # Join a queue and generate a token
    path(
        "join/",
        JoinQueueAPIView.as_view(),
        name="queue-join",
    ),

    # Check token status using its UUID
    path(
        "tokens/<uuid:public_id>/",
        TokenStatusAPIView.as_view(),
        name="token-status",
    ),

    # Cancel a waiting token using its UUID
    path(
        "tokens/<uuid:public_id>/cancel/",
        CancelTokenAPIView.as_view(),
        name="token-cancel",
    ),
]
