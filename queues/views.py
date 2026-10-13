
from django.db import transaction
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from organizations.models import Service
from .models import Queue, Token
from .serializers import QueueSerializer, TokenSerializer


ACTIVE_STATUSES = [
    Token.Status.WAITING,
    Token.Status.CALLED,
    Token.Status.SERVING,
]


class QueueListAPIView(generics.ListAPIView):
    serializer_class = QueueSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Queue.objects.filter(
            is_active=True,
            service__is_active=True,
            service__organization__is_active=True,
        ).select_related("service", "service__organization")


class JoinQueueAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        customer_name = request.data.get("customer_name", "").strip()
        queue_id = request.data.get("queue")

        if not customer_name:
            return Response(
                {"error": "Customer name is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(customer_name) > 150:
            return Response(
                {"error": "Customer name cannot exceed 150 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not queue_id:
            return Response(
                {"error": "Queue ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queue = get_object_or_404(
            Queue.objects.select_related("service"),
            pk=queue_id,
            is_active=True,
            service__is_active=True,
            service__organization__is_active=True,
        )

        with transaction.atomic():
            # Lock the queue row while allocating a token.
            # SQLite does not provide the same row-level locking
            # as PostgreSQL, so use PostgreSQL for production.
            locked_queue = Queue.objects.select_for_update().get(
                pk=queue.pk
            )

            last_number = (
                Token.objects.filter(queue=locked_queue)
                .aggregate(max_number=Max("token_number"))["max_number"]
                or 0
            )

            token = Token.objects.create(
                queue=locked_queue,
                token_number=last_number + 1,
                customer_name=customer_name,
                status=Token.Status.WAITING,
            )

        return Response(
            TokenSerializer(token).data,
            status=status.HTTP_201_CREATED,
        )


class TokenStatusAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token_id):
        token = get_object_or_404(
            Token.objects.select_related("queue", "queue__service"),
            pk=token_id,
        )

        ahead = Token.objects.filter(
            queue=token.queue,
            token_number__lt=token.token_number,
            status__in=[
                Token.Status.WAITING,
                Token.Status.CALLED,
                Token.Status.SERVING,
            ],
        ).count()

        if token.status in [
            Token.Status.COMPLETED,
            Token.Status.CANCELLED,
            Token.Status.NO_SHOW,
        ]:
            position = None
            estimated_wait = 0
        else:
            position = ahead + 1
            service_minutes = token.queue.service.average_service_time
            estimated_wait = ahead * service_minutes

        return Response({
            "token_id": token.id,
            "token_number": token.token_number,
            "customer_name": token.customer_name,
            "queue": token.queue.name,
            "status": token.status,
            "people_ahead": ahead,
            "position": position,
            "estimated_wait_minutes": estimated_wait,
            "checked_at": timezone.now(),
        })


class CancelTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token_id):
        with transaction.atomic():
            token = get_object_or_404(
                Token.objects.select_for_update(),
                pk=token_id,
            )

            if token.status != Token.Status.WAITING:
                return Response(
                    {
                        "error": (
                            "Only waiting tokens can be cancelled."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token.status = Token.Status.CANCELLED
            token.save(update_fields=["status"])

        return Response(
            {
                "message": "Token cancelled successfully.",
                "token_id": token.id,
                "status": token.status,
            },
            status=status.HTTP_200_OK,
        )
