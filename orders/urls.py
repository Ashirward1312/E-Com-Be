# from django.urls import path

# from .views import (
#     CheckoutView,
#     MyOrdersView,
#     OrderDetailView,
#     CancelOrderView,
#     AdminOrderListView,
#     AdminOrderDetailView,
#     UpdateOrderStatusView,
#     AdminDashboardView
# )

# urlpatterns = [

#     path(
#         "checkout/",
#         CheckoutView.as_view(),
#     ),

#     # ---------- Admin ----------

#     path(
#         "admin/dashboard/",
#         AdminDashboardView.as_view(),
#     ),

#     path(
#         "admin/",
#         AdminOrderListView.as_view(),
#     ),

#     path(
#         "admin/<str:order_id>/",
#         AdminOrderDetailView.as_view(),
#     ),

#     path(
#         "admin/<str:order_id>/status/",
#         UpdateOrderStatusView.as_view(),
#     ),

#     # ---------- User ----------

#     path(
#         "",
#         MyOrdersView.as_view(),
#     ),

#     path(
#         "<str:order_id>/",
#         OrderDetailView.as_view(),
#     ),

#     path(
#         "<str:order_id>/cancel/",
#         CancelOrderView.as_view(),
#     ),
# ]


from django.urls import path

from .views import (
    CheckoutView,
    MyOrdersView,
    OrderDetailView,
    CancelOrderView,
    AdminOrderListView,
    AdminOrderDetailView,
    UpdateOrderStatusView,
    AdminDashboardView,
    DownloadEbookView,
)

urlpatterns = [

    # ---------- Checkout ----------

    path(
        "checkout/",
        CheckoutView.as_view(),
    ),

    # ---------- Download ----------

    path(
        "download/<int:order_item_id>/",
        DownloadEbookView.as_view(),
        name="download-ebook",
    ),

    # ---------- Admin ----------

    path(
        "admin/dashboard/",
        AdminDashboardView.as_view(),
    ),

    path(
        "admin/",
        AdminOrderListView.as_view(),
    ),

    path(
        "admin/<str:order_id>/",
        AdminOrderDetailView.as_view(),
    ),

    path(
        "admin/<str:order_id>/status/",
        UpdateOrderStatusView.as_view(),
    ),

    # ---------- User ----------

    path(
        "",
        MyOrdersView.as_view(),
    ),

    path(
        "<str:order_id>/",
        OrderDetailView.as_view(),
    ),

    path(
        "<str:order_id>/cancel/",
        CancelOrderView.as_view(),
    ),
]
