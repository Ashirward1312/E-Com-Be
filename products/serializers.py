from rest_framework import serializers
from .models import Product, Category, ProductImage, Coupon


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    # Return the full absolute URL so frontend can use it directly
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return f"http://127.0.0.1:8000{obj.image.url}"
        return None


class ProductSerializer(serializers.ModelSerializer):
    # Nested gallery images (ProductImage model)
    images = ProductImageSerializer(many=True, read_only=True)
    # Single image field — override to return absolute URL
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        # ✅ Explicit fields avoids conflict between model field 'image'
        # and our SerializerMethodField 'image'
        fields = [
            'id', 'category', 'name', 'description',
            'price', 'stock', 'image', 'images',
            'created_at', 'created_by',
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return f"http://127.0.0.1:8000{obj.image.url}"
        return None


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"