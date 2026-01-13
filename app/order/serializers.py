from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import serializers

from app.account.models import Account, Address
from app.order.models import Order, OrderItem
from app.product.models import Product
from app.store.models import Store
from app.utils import BaseSerializer


def calculate_effective_price(product: Product) -> Decimal:
    price = Decimal(product.price or 0)
    discount = Decimal(product.discount_percentage or 0)
    effective = price * (Decimal(1) - (discount / Decimal(100)))
    return effective.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class OrderItemInputSerializer(serializers.Serializer):

    product_uuid = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):

    # Nested serializers
    items = OrderItemInputSerializer(many=True)

    # Fields
    store_uuid = serializers.UUIDField()
    account_uuid = serializers.UUIDField()
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    zip_code = serializers.CharField()
    street = serializers.CharField()
    number = serializers.CharField()
    neighborhood = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    complement = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    reference = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    city = serializers.CharField()
    state = serializers.CharField()
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        allow_null=True,
    )
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        allow_null=True,
    )

    @transaction.atomic
    def create(self, validated_data):
        account = get_object_or_404(Account, uuid=validated_data["account_uuid"])
        store = get_object_or_404(Store, uuid=validated_data["store_uuid"])

        items = validated_data.pop("items", [])
        if not items:
            raise serializers.ValidationError("Must contain at least one item.")

        merged_items = {}
        for item in items:
            merged_items[item["product_uuid"]] = merged_items.get(item["product_uuid"], 0) + item["quantity"]

        product_uuids = list(merged_items.keys())
        products = get_list_or_404(
            Product,
            uuid__in=product_uuids,
            store=store,
            is_active=True,
        )

        found_products = {p.uuid: p for p in products}
        if missing_products := [str(uuid) for uuid in product_uuids if uuid not in found_products]:
            raise serializers.ValidationError(f"Products not found or inactive: {', '.join(missing_products)}")

        if not validated_data.get("zip_code") or not validated_data.get("street") or not validated_data.get("number"):
            raise serializers.ValidationError("Delivery address fields are required.")

        # Create order
        order = Order.objects.create(
            store=store,
            account=account,
            status=Order.STATUS_PENDING,
            notes=validated_data.get("notes"),
            delivery_fee=store.delivery_fee,
            zip_code=validated_data.get("zip_code"),
            street=validated_data.get("street"),
            number=validated_data.get("number"),
            neighborhood=validated_data.get("neighborhood"),
            complement=validated_data.get("complement"),
            reference=validated_data.get("reference"),
            city=validated_data.get("city"),
            state=validated_data.get("state"),
            latitude=validated_data.get("latitude"),
            longitude=validated_data.get("longitude"),
        )

        # Create order items
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product_uuid=product.uuid,
                    product_name=product.name,
                    unit_price=calculate_effective_price(product),
                    quantity=merged_items[product.uuid],
                )
                for product in products
            ]
        )
        # Recalculate totals
        order.recalculate_totals()

        min_order_value = Decimal(store.min_order_value or 0)
        if order.subtotal < min_order_value:
            raise serializers.ValidationError(
                f"Order subtotal {order.subtotal} is below the minimum order value of {min_order_value}."
            )

        order.save(update_fields=["subtotal", "total"])
        return order


class OrderItemSerializer(BaseSerializer):

    # Fields
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        exclude = BaseSerializer.Meta.exclude

    def get_total(self, obj: OrderItem) -> Decimal:
        return (obj.unit_price or Decimal("0.00")) * (obj.quantity or 0)


class OrderSerializer(BaseSerializer):

    # Nested serializers
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        exclude = BaseSerializer.Meta.exclude
