from .models import Order
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import NotFound
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.db.models import Q


from cart.models import Cart
from .models import (
    Order,
    OrderItem,
    OrderStatusHistory,
)
from .serializers import OrderSerializer

from decimal import Decimal

from rest_framework.permissions import IsAdminUser

from accounts.models import User
from products.models import Product


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            raise ValidationError("Cart is empty.")

        cart_items = cart.items.select_related("product")

        if not cart_items.exists():
            raise ValidationError("Cart is empty.")

        required_fields = [
            "full_name",
            "phone",
            "email",
            "address",
            "city",
            "state",
            "pincode",
        ]

        for field in required_fields:
            if not request.data.get(field):
                raise ValidationError(f"{field} is required.")

        total_price = 0
        for item in cart_items:

            product = item.product


        if not product.is_active:
         raise ValidationError({
            "product_error": f"{product.name} is currently unavailable."
            })

            # ✅ HANDLE ZERO STOCK FIRST
        if product.stock <= 0:
            raise ValidationError({
                "stock_error": f"{product.name} is out of stock."
            })

             # ✅ THEN CHECK QUANTITY
        if item.quantity > product.stock:
            raise ValidationError({
                "stock_error": f"Only {product.stock} item(s) available for {product.name}."
            })

        total_price += product.price * item.quantity


        discount_amount = 0
        final_price = total_price - discount_amount

        order = Order.objects.create(
            user=request.user,
            full_name=request.data["full_name"],
            phone=request.data["phone"],
            email=request.data["email"],
            address=request.data["address"],
            city=request.data["city"],
            state=request.data["state"],
            pincode=request.data["pincode"],
            payment_method=request.data.get(
                "payment_method",
                "cod",
            ),
            payment_status="pending",
            total_price=total_price,
            discount_amount=discount_amount,
            final_price=final_price,
            status="placed",
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

            item.product.stock -= item.quantity
            item.product.save()

        OrderStatusHistory.objects.create(
            order=order,
            status="placed",
        )

        cart.items.all().delete()

        serializer = OrderSerializer(
            order,
            context={"request": request},
        )

        return Response(
            {
                "message":"Order placed successfully.",
                "order":serializer.data,
                "order_id":order.order_id
            },
        status=status.HTTP_201_CREATED
        )


class MyOrdersView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(
                user=self.request.user
            )
            .prefetch_related(
                "items",
                "status_history",
            )
            .order_by("-created_at")
        )


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return (
                Order.objects
                .prefetch_related(
                    "items",
                    "status_history",
                )
                .get(
                order_id=self.kwargs["order_id"],
                user=self.request.user,
                  )
            )
        except Order.DoesNotExist:
            raise NotFound("Order not found.")


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):

        try:
            order = Order.objects.prefetch_related(
                "items"
            ).get(
                order_id=order_id,
                user=request.user,
            )
        except Order.DoesNotExist:
            raise NotFound("Order not found.")

        if order.status not in [
            "placed",
            "confirmed",
        ]:
            raise ValidationError(
                "This order cannot be cancelled."
            )

        order.status = "cancelled"
        order.save(update_fields=["status"])

        OrderStatusHistory.objects.create(
            order=order,
            status="cancelled",
        )

        for item in order.items.all():
            product = item.product

            if product:
                product.stock += item.quantity
                product.save(update_fields=["stock"])

        return Response(
            {
                "message": "Order cancelled successfully."
            },
            status=status.HTTP_200_OK,
        )


class AdminOrderListView(ListAPIView):
    
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = (
            Order.objects
            .select_related("user")
            .prefetch_related(
                "items",
                "status_history",
            )
            .order_by("-created_at")
        )

        status = self.request.query_params.get("status")
        payment_status = self.request.query_params.get("payment_status")
        payment_method = self.request.query_params.get("payment_method")
        search = self.request.query_params.get("search")

        if status:
            queryset = queryset.filter(status=status)

        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)

        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        if search:
            queryset=queryset.filter(
            Q(order_id__icontains=search)|
            Q(full_name__icontains=search)|
            Q(phone__icontains=search)|
            Q(email__icontains=search)
            )

        return queryset


from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import NotFound

from .models import Order
from .serializers import OrderSerializer


class AdminOrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

    def get_object(self):

        try:
            return (
                Order.objects
                .prefetch_related(
                    "items",
                    "status_history",
                )
                .get(
                    order_id=self.kwargs["order_id"]
                )
            )

        except Order.DoesNotExist:
            raise NotFound("Order not found.")
        

class UpdateOrderStatusView(APIView):

    permission_classes = [IsAdminUser]

    ALLOWED_STATUS = [
        "placed",
        "confirmed",
        "packed",
        "shipped",
        "delivered",
        "cancelled",
    ]

    def patch(self, request, order_id):

        try:
            order = Order.objects.get(
                order_id=order_id
            )

        except Order.DoesNotExist:
            raise NotFound("Order not found.")

        new_status = request.data.get("status")

        if new_status not in self.ALLOWED_STATUS:
            raise ValidationError(
                "Invalid status."
            )

        if order.status == new_status:
            raise ValidationError(
                "Order already has this status."
            )

        order.status = new_status
        order.save(update_fields=["status"])

        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
        )

        serializer = OrderSerializer(
            order,
            context={"request": request},
        )

        return Response(
            {
                "message": "Order status updated successfully.",
                "order": serializer.data,
            },
            status=status.HTTP_200_OK,
        )        



class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):

        total_products = Product.objects.filter(
            is_active=True
        ).count()

        total_orders = Order.objects.count()

        total_users = User.objects.count()

        total_revenue = (
            Order.objects.filter(
                payment_status="paid"
            )
            .values_list(
                "final_price",
                flat=True,
            )
        )

        revenue = sum(
            total_revenue,
            Decimal("0.00"),
        )

        return Response({
            "total_products": total_products,
            "total_orders": total_orders,
            "total_users": total_users,
            "total_revenue": revenue,
        })    