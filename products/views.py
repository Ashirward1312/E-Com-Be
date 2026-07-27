from rest_framework import generics
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import Product
from .serializers import ProductSerializer, CouponSerializer
from .models import Coupon
from rest_framework.generics import ListCreateAPIView


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]


class CouponCreateView(generics.CreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]

class AdminCouponListCreateView(ListCreateAPIView):
    queryset = Coupon.objects.all().order_by("-id")
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]