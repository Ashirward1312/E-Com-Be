from django.urls import path

from .views import (
    AdminCategoryDetailView,
    AdminCategoryListCreateView,
    AdminCouponListCreateView,
    CategoryListView,
    LatestProductView,
    ProductDetailView,
    ProductListCreateView,
)
urlpatterns = [

    # Products

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

    # Public Categories

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

    # ---------- Admin Categories ----------

    path(
        "admin/categories/",
        AdminCategoryListCreateView.as_view(),
        name="admin-category-list-create",
    ),

    path(
        "admin/categories/<int:pk>/",
        AdminCategoryDetailView.as_view(),
        name="admin-category-detail",
    ),

    # ---------- Admin Coupons ----------

    path(
        "admin/coupons/",
        AdminCouponListCreateView.as_view(),
        name="admin-coupons",
    ),
]
