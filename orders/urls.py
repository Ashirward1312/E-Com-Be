from django.urls import path

from .views import (
    CheckoutView,
    MyOrdersView,
    OrderDetailView,
    CancelOrderView,
    AdminOrderListView,
    AdminOrderDetailView,
    UpdateOrderStatusView,
    AdminDashboardView
)

urlpatterns = [

    path(
        "checkout/",
        CheckoutView.as_view(),
        name="checkout",
    ),

    path(
        "",
        MyOrdersView.as_view(),
        name="my-orders",
    ),

    path(
        "<str:order_id>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),

    path(
        "<str:order_id>/cancel/",
        CancelOrderView.as_view(),
        name="cancel-order",
    ),

    # ---------- Admin ----------

    path(
        "admin/dashboard/",
        AdminDashboardView.as_view(),
        name="admin-dashboard",
    ),

    path(
        "admin/",
        AdminOrderListView.as_view(),
        name="admin-orders",
    ),

    path(
        "admin/<str:order_id>/",
        AdminOrderDetailView.as_view(),
        name="admin-order-detail",
    ),

    path(
        "admin/<str:order_id>/status/",
        UpdateOrderStatusView.as_view(),
        name="update-order-status",
    ),
]