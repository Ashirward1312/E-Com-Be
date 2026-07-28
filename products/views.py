

from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

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

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    search_fields = [
        "name",
        "description",
    ]
    filter_backends = [
        SearchFilter,
        OrderingFilter,
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
