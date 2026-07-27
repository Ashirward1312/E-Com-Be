# from rest_framework import generics
# from rest_framework.permissions import IsAdminUser, AllowAny
# from .models import Product
# from .serializers import ProductSerializer, CouponSerializer
# from .models import Coupon
# from rest_framework.generics import ListCreateAPIView


# class ProductListCreateView(generics.ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def get_permissions(self):
#         if self.request.method == 'POST':
#             return [IsAdminUser()]
#         return [AllowAny()]

#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)


# class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def get_permissions(self):
#         if self.request.method in ['PUT', 'PATCH', 'DELETE']:
#             return [IsAdminUser()]
#         return [AllowAny()]


# class CouponCreateView(generics.CreateAPIView):
#     queryset = Coupon.objects.all()
#     serializer_class = CouponSerializer
#     permission_classes = [IsAdminUser]

# class AdminCouponListCreateView(ListCreateAPIView):
#     queryset = Coupon.objects.all().order_by("-id")
#     serializer_class = CouponSerializer
#     permission_classes = [IsAdminUser]


from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAdminUser

from .models import Category, Coupon, Product
from .serializers import (
    CategorySerializer,
    CouponSerializer,
    ProductSerializer,
)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "price",
        "created_at",
    ]

    ordering = [
        "-created_at",
    ]

    def get_queryset(self):
        if self.request.method == "POST":
            return Product.objects.all()

        queryset = Product.objects.filter(
            is_active=True
        ).select_related("category")

        category = self.request.query_params.get("category")

        if category:
            queryset = queryset.filter(category_id=category)

        return queryset

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return Product.objects.all()

        return Product.objects.filter(
            is_active=True
        ).select_related("category")

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [AllowAny()]


class LatestProductView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True
        ).select_related("category").order_by("-created_at")[:10]


class AdminCouponListCreateView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all().order_by("-id")
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]
