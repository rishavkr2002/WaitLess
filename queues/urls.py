
from django.urls import path

from .views import (
    CancelTokenAPIView,
    JoinQueueAPIView,
    QueueListAPIView,
    TokenStatusAPIView,
)

urlpatterns = [
    path("", QueueListAPIView.as_view(), name="queue-list"),
    path("join/", JoinQueueAPIView.as_view(), name="queue-join"),
    path(
        "tokens/<int:token_id>/",
        TokenStatusAPIView.as_view(),
        name="token-status",
    ),
    path(
        "tokens/<int:token_id>/cancel/",
        CancelTokenAPIView.as_view(),
        name="token-cancel",
    ),
]
