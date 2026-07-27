from django.urls import path
from .views import AddToCartView, ViewCartView, RemoveFromCartView, UpdateCartItemView,ApplyCouponView,AdminCustomerOrdersView
from .views import CheckoutView
from .views import OrderListView, OrderDetailView,CancelOrderView,AdminUpdateOrderStatus,AdminOrderListView,AdminCustomerListView
urlpatterns = [
    path('add/', AddToCartView.as_view(), name='add-to-cart'),
    path('', ViewCartView.as_view(), name='view-cart'),
    path('remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('update/<int:item_id>/', UpdateCartItemView.as_view(), name='update-cart-item'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path("apply-coupon/", ApplyCouponView.as_view(), name="apply-coupon"),
    path("orders/<int:pk>/cancel/", CancelOrderView.as_view()),
    path("admin/orders/<int:pk>/status/", AdminUpdateOrderStatus.as_view()),
    path("admin/orders/", AdminOrderListView.as_view()),
    path("admin/customers/", AdminCustomerListView.as_view()),
    path("admin/customer-orders/<int:pk>/", AdminCustomerOrdersView.as_view()),
]
