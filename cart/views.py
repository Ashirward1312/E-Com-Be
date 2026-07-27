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

# ✅ सही इम्पोर्ट्स (Correct Imports)
from django.contrib.auth import get_user_model
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from products.models import Product, Coupon

# ✅ User मॉडल को सही तरीके से प्राप्त करना
User = get_user_model()


# ✅ Add To Cart (User must be logged in for this logic)
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated] # Changed to IsAuthenticated to ensure request.user exists

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound("Product not found")

        # get_or_create ensures a cart exists for the user
        cart, _ = Cart.objects.get_or_create(user=request.user)

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
        # get_or_create is safer in case a user has no cart yet
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
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
            # For removing item, user should use the remove endpoint
            raise ValidationError("Quantity must be greater than 0.")
        serializer.save(quantity=quantity)


# ✅ Apply Coupon
class ApplyCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")
        if not code:
            raise ValidationError("Coupon code is required.")
        try:
            coupon = Coupon.objects.get(code__iexact=code, active=True)
        except Coupon.DoesNotExist:
            raise ValidationError("Invalid or expired coupon.")

        cart = Cart.objects.get(user=request.user)

        total = 0
        for item in cart.items.all():
            total += item.product.price * item.quantity

        discount_amount = (total * coupon.discount_percentage) / 100
        final_total = total - discount_amount

        return Response({
            "message": "Coupon applied successfully!",
            "original_total": total,
            "discount_amount": discount_amount,
            "final_total": final_total,
        })


# ✅ ✅ ✅ FINAL CHECKOUT WITH STOCK REDUCE
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Your cart could not be found."}, status=400)

        if not cart.items.exists():
            return Response({"error": "Your cart is empty."}, status=400)

        # Shipping data from the frontend
        shipping_data = {
            "full_name": request.data.get("full_name"),
            "phone": request.data.get("phone"),
            "email": request.data.get("email"),
            "address": request.data.get("address"),
        }
        if not all(shipping_data.values()):
            return Response({"error": "Shipping information is incomplete."}, status=400)

        total = 0
        for item in cart.items.all():
            total += item.product.price * item.quantity

        discount = 0
        final_total = total
        coupon_code = request.data.get("coupon")

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
                discount = (total * coupon.discount_percentage) / 100
                final_total = total - discount
                # Note: Deactivating coupon should be considered carefully.
                # Maybe just track its usage instead.
                # coupon.active = False
                # coupon.save()
            except Coupon.DoesNotExist:
                return Response({"error": "Invalid Coupon"}, status=400)

        # Create Order with all required fields from the new model
        order = Order.objects.create(
            user=request.user,
            total_price=total,
            discount_amount=discount,
            final_price=final_total,
            **shipping_data
        )

        for item in cart.items.all():
            product = item.product
            if product.stock < item.quantity:
                # This should ideally be a transaction that rolls back
                order.delete() # Clean up the created order if stock check fails
                return Response({"error": f"Sorry, {product.name} is out of stock."}, status=400)

            product.stock -= item.quantity
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price,
            )

        cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response({
            "message": "Order placed successfully!",
            "order": serializer.data
        })


# ✅ User Orders List
class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


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
            raise NotFound("Order not found")

        if order.status in ["shipped", "delivered"]:
            return Response({"error": "Cannot cancel an order that has already been shipped or delivered."}, status=400)

        if order.status == "cancelled":
             return Response({"message": "Order is already cancelled."}, status=200)

        order.status = "cancelled"
        order.save()

        # Optional: Restore stock for cancelled orders
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()

        return Response({"message": "Your order has been cancelled."})


# ✅ Admin: Get All Orders
class AdminOrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Order.objects.all().order_by("-created_at")


# ✅ Admin: Update Order Status
class AdminUpdateOrderStatus(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            raise NotFound("Order not found")

        status = request.data.get("status")
        if status not in [choice[0] for choice in Order.STATUS_CHOICES]:
            return Response({"error": "Invalid status provided."}, status=400)

        order.status = status
        order.save()
        return Response({"message": f"Order status updated to {status}."})


# ✅ Admin: List all Customers
class AdminCustomerListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # We filter for users who have placed at least one order
        users_with_orders = User.objects.filter(order__isnull=False).distinct()
        data = []

        for user in users_with_orders:
            orders = Order.objects.filter(user=user)
            total_spent = sum(o.final_price for o in orders)

            data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "orders_count": orders.count(),
                "total_spent": total_spent,
            })
        
        return Response(data)


class AdminOrderListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        orders = Order.objects.all().order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class AdminCustomerListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()

        data = []

        for user in users:
            orders = Order.objects.filter(user=user)

            total_spent = sum(
                order.final_price or order.total_price
                for order in orders
            )

            data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "orders_count": orders.count(),
                "total_spent": total_spent,
            })

        return Response(data)


class AdminCustomerOrdersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        orders = Order.objects.filter(user_id=pk)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)



class AdminCustomerListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        data = []

        for user in users:
            orders = Order.objects.filter(user=user)

            order_data = []
            total_spent = 0

            for order in orders:
                total_spent += order.final_price or order.total_price

                order_data.append({
                    "order_id": order.order_id,
                    "status": order.status,
                    "payment_status": order.payment_status,
                    "total": order.final_price or order.total_price,
                    "shipping_address": order.address,
                    "phone": order.phone,
                    "email": order.email,
                })

            data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "orders_count": orders.count(),
                "total_spent": total_spent,
                "orders": order_data,
            })

        return Response(data)