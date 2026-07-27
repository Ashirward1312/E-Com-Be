from django.urls import path

from .views import (
    AddToCartView,
    ViewCartView,
    UpdateCartItemView,
    RemoveFromCartView,
    ClearCartView,
)

urlpatterns = [
    path(
        "",
        ViewCartView.as_view(),
        name="view-cart",
    ),

    path(
        "add/",
        AddToCartView.as_view(),
        name="add-to-cart",
    ),

    path(
        "item/<int:item_id>/",
        UpdateCartItemView.as_view(),
        name="update-cart-item",
    ),

    path(
        "item/<int:item_id>/delete/",
        RemoveFromCartView.as_view(),
        name="remove-cart-item",
    ),

    path(
        "clear/",
        ClearCartView.as_view(),
        name="clear-cart",
    ),
]
