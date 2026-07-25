from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.generics import (
    RetrieveAPIView,
    DestroyAPIView,
    UpdateAPIView,
    ListAPIView,
)
from rest_framework.exceptions import NotFound, ValidationError
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from products.models import Product, Coupon


# ✅ Add To Cart (Guest Allowed)
class AddToCartView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        product = Product.objects.get(id=product_id)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product
        )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        return Response({"message": "Product added to cart"})


# ✅ View Cart
class ViewCartView(RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


# ✅ Remove Item
class RemoveFromCartView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        item_id = self.kwargs.get("item_id")

        try:
            return CartItem.objects.get(
                id=item_id, cart__user=self.request.user
            )
        except CartItem.DoesNotExist:
            raise NotFound("Item not found in your cart")


# ✅ Update Quantity
class UpdateCartItemView(UpdateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        item_id = self.kwargs.get("item_id")

        try:
            return CartItem.objects.get(
                id=item_id, cart__user=self.request.user
            )
        except CartItem.DoesNotExist:
            raise NotFound("Item not found in your cart")

    def perform_update(self, serializer):
        quantity = int(self.request.data.get("quantity"))

        if quantity <= 0:
            raise ValidationError("Quantity must be greater than 0")

        serializer.save(quantity=quantity)


# ✅ Apply Coupon
class ApplyCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")

        try:
            coupon = Coupon.objects.get(code=code, active=True)
        except Coupon.DoesNotExist:
            raise ValidationError("Invalid Coupon")

        cart = Cart.objects.get(user=request.user)

        total = 0
        for item in cart.items.all():
            total += item.product.price * item.quantity

        discount_amount = (total * coupon.discount_percentage) / 100
        final_total = total - discount_amount

        return Response(
            {
                "original_total": total,
                "discount": discount_amount,
                "final_total": final_total,
            }
        )


# ✅ ✅ ✅ FINAL CHECKOUT WITH STOCK REDUCE
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart is empty"}, status=400)

        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total = 0
        for item in cart.items.all():
            total += item.product.price * item.quantity

        discount = 0
        final_total = total

        coupon_code = request.data.get("coupon")

        if coupon_code:
            try:
                coupon = Coupon.objects.get(
                    code=coupon_code, active=True
                )
                discount = (total * coupon.discount_percentage) / 100
                final_total = total - discount

                coupon.active = False
                coupon.save()

            except Coupon.DoesNotExist:
                return Response(
                    {"error": "Invalid Coupon"}, status=400
                )

        # ✅ Create Order
        order = Order.objects.create(
            user=request.user,
            total_price=total,
            discount_amount=discount,
            final_price=final_total,
        )

        # ✅ STOCK CHECK + REDUCE + CREATE ORDER ITEMS
        for item in cart.items.all():

            product = item.product

            # ✅ Stock Validation
            if product.stock < item.quantity:
                return Response(
                    {"error": f"{product.name} is out of stock"},
                    status=400,
                )

            # ✅ Reduce Stock
            product.stock -= item.quantity
            product.save()

            # ✅ Create Order Item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price,
            )

        # ✅ Clear Cart
        cart.items.all().delete()

        return Response(
            {
                "message": "Order placed successfully",
                "final_price": final_total,
            }
        )


# ✅ User Orders List
class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


# ✅ Order Detail
class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# ✅ Cancel Order
class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=404
            )

        if order.status in ["shipped", "delivered"]:
            return Response(
                {
                    "error": "Cannot cancel shipped/delivered order"
                },
                status=400,
            )

        order.status = "cancelled"
        order.save()

        return Response({"message": "Order cancelled"})


# ✅ Admin Update Order Status
class AdminUpdateOrderStatus(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=404
            )

        status = request.data.get("status")

        if status not in dict(Order.STATUS_CHOICES):
            return Response(
                {"error": "Invalid status"}, status=400
            )

        order.status = status
        order.save()

        return Response({"message": "Status updated"})