from rest_framework import serializers

from .models import (
    Order,
    OrderItem,
    OrderStatusHistory,
)

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    product_image = serializers.SerializerMethodField()

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_image",
            "quantity",
            "price",
            "subtotal",
        ]

    def get_product_image(self, obj):
        request = self.context.get("request")

        if obj.product and obj.product.image:
            if request:
                return request.build_absolute_uri(
                    obj.product.image.url
                )
            return obj.product.image.url

        return None

    def get_subtotal(self, obj):
        return obj.price * obj.quantity


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = [
            "status",
            "created_at",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    status_history = OrderStatusHistorySerializer(
        many=True,
        read_only=True,
    )

    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_id",
            "full_name",
            "phone",
            "email",
            "address",
            "city",
            "state",
            "pincode",
            "payment_method",
            "payment_status",
            "total_price",
            "discount_amount",
            "final_price",
            "total_items",
            "status",
            "created_at",
            "updated_at",
            "items",
            "status_history",
      ]

    def get_total_items(self, obj):
        return sum(
            item.quantity
            for item in obj.items.all()
        )
