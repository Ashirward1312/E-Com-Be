from .serializers import CartSyncSerializer
from rest_framework.exceptions import ValidationError
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import (
    DestroyAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import Cart, CartItem
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    CartSyncSerializer
)



class AddToCartView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):

        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if quantity <= 0:
            raise ValidationError("Quantity must be greater than 0.")

        try:
            product = Product.objects.get(
                id=product_id,
                is_active=True,
            )
        except Product.DoesNotExist:
            raise NotFound("Product not found.")

        if product.stock < quantity:
            return Response(
                {"error": "Insufficient stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
        )

        if created:
            cart_item.quantity = quantity
        else:
            if (cart_item.quantity + quantity) > product.stock:
                return Response(
                    {"error": "Stock limit exceeded."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cart_item.quantity += quantity

        cart_item.save()

        return Response({"message": "Product added to cart."})


class ViewCartView(RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class UpdateCartItemView(UpdateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return CartItem.objects.get(
                id=self.kwargs["item_id"],
                cart__user=self.request.user,
            )
        except CartItem.DoesNotExist:
            raise NotFound("Cart item not found.")

    def perform_update(self, serializer):

        quantity = int(self.request.data.get("quantity"))

        if quantity <= 0:
            raise ValidationError("Quantity must be greater than 0.")

        product = serializer.instance.product

        if quantity > product.stock:
            raise ValidationError("Requested quantity exceeds stock.")

        serializer.save(quantity=quantity)


class RemoveFromCartView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return CartItem.objects.get(
                id=self.kwargs["item_id"],
                cart__user=self.request.user,
            )
        except CartItem.DoesNotExist:
            raise NotFound("Cart item not found.")


class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart.items.all().delete()

        return Response({"message": "Cart cleared successfully."})


class CartSyncView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        items = request.data.get("items", [])

        if not items:
            raise ValidationError("Cart is empty.")

        serializer = CartSyncSerializer(
            data=items,
            many=True,
        )

        serializer.is_valid(raise_exception=True)

        cart, _ = Cart.objects.get_or_create(
            user=request.user
        )

        # Purana cart hata do
        cart.items.all().delete()

        for item in serializer.validated_data:

            try:
                product = Product.objects.get(
                    id=item["product_id"],
                    is_active=True,
                )
            except Product.DoesNotExist:
                raise ValidationError(
                    f"Product {item['product_id']} not found."
                )

            if item["quantity"] > product.stock:
                raise ValidationError(
                    f"Only {product.stock} item(s) available for {product.name}."
                )

            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=item["quantity"],
            )

        return Response(
            {
                "message": "Cart synced successfully."
            },
            status=status.HTTP_200_OK,
        )
