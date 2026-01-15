from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from app.order.models import Order, OrderItem
from app.order.serializers import OrderCreateSerializer, OrderSerializer
from app.utils import BaseModelViewSet


class OrderViewSet(BaseModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.select_related(
        "account",
        "account__user",
        "store",
    ).prefetch_related("items")
    serializer_class = OrderSerializer

    def get_queryset(self):
        """Return orders belonging to the authenticated user's account."""
        return self.queryset.filter(
            account=self.request.user.account,
        ).order_by("-created_at")

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == "create":
            return OrderCreateSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        """Handle order creation."""
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
