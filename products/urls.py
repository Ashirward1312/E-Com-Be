from django.urls import path
from .views import ProductListCreateView, ProductDetailView, CouponCreateView,AdminCouponListCreateView

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('coupons/', CouponCreateView.as_view(), name='create-coupon'),
    path("admin/coupons/", AdminCouponListCreateView.as_view()),
]