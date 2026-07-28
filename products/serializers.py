from rest_framework import serializers
from .models import Product, Category, ProductImage, Coupon


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage    
        fields = [
            "id",
            "image",
        ]

    def get_image(self, obj):
        request = self.context.get("request")

        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url

        return None


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
    )

    image = serializers.SerializerMethodField(read_only=True)

    upload_image = serializers.ImageField(
        source="image",
        write_only=True,
        required=False,
        allow_null=True
    )

    images = ProductImageSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "category_id",
            "name",
            "slug",
            "description",
            "price",
            "stock",
           "image",
            "upload_image",
            "images",
            "is_active",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "slug",
            "created_at",
            "updated_at",
        ]
    def get_image(self, obj):
            request = self.context.get("request")
    
            if obj.image:
                if request:
                    return request.build_absolute_uri(obj.image.url)
                return obj.image.url
    
            return None
        


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "discount_percentage",
            "active",
        ]
