from django.contrib import admin

from .models import (
    Order,
    OrderItem,
    OrderStatusHistory,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        "product",
        "quantity",
        "price",
        "download_count",
        "last_downloaded_at",
    )


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0

    readonly_fields = (
        "status",
        "created_at",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_id",
        "user",
        "final_price",
        "payment_method",
        "payment_status",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "order_id",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "order_id",
        "created_at",
        "updated_at",
    )

    inlines = [
        OrderItemInline,
        OrderStatusHistoryInline,
    ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "product",
        "price",
        "download_count",
        "last_downloaded_at",
    )

    search_fields = (
        "order__order_id",
        "product__name",
    )


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "order__order_id",
    )
