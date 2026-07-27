from django.urls import path

from .views import (
    AdminCouponListCreateView,
    CategoryListView,
    LatestProductView,
    ProductDetailView,
    ProductListCreateView,
)

urlpatterns = [
    path(
        "",
        ProductListCreateView.as_view(),
        name="product-list",
    ),

    path(
        "latest/",
        LatestProductView.as_view(),
        name="latest-products",
    ),

    path(
        "categories/",
        CategoryListView.as_view(),
        name="category-list",
    ),

    path(
        "<int:pk>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),

    path(
        "admin/coupons/",
        AdminCouponListCreateView.as_view(),
        name="admin-coupons",
    ),
]
