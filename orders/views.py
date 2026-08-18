
from decimal import Decimal
from products.models import Product
from accounts.models import User
from django.http import FileResponse
from django.db.models import Q
from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    NotFound,
)
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import (
    IsAuthenticated, IsAdminUser
)
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from .models import (
    Order,
    OrderItem,
    OrderStatusHistory,
)
from .serializers import OrderSerializer, LibrarySerializer
from django.conf import settings

from .services import create_razorpay_order
import razorpay
from django.conf import settings


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        try:
            cart = Cart.objects.get(
                user=request.user
            )

        except Cart.DoesNotExist:
            raise ValidationError(
                "Cart is empty."
            )

        cart_items = cart.items.select_related(
            "product"
        )

        if not cart_items.exists():
            raise ValidationError(
                "Cart is empty."
            )

        total_price = 0

        for item in cart_items:

            product = item.product

            if not product:
                raise ValidationError(
                    "Invalid product."
                )

            if not product.is_active:
                raise ValidationError(
                    f"{product.name} is unavailable."
                )

            total_price += (
                product.price * item.quantity
            )

        discount_amount = 0

        final_price = (
            total_price - discount_amount
        )

        order = Order.objects.create(
            user=request.user,
            payment_method="online",
            payment_status="pending",
            total_price=total_price,
            discount_amount=discount_amount,
            final_price=final_price,
            status="pending",
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=1,
                price=item.product.price,
            )

        OrderStatusHistory.objects.create(
            order=order,
            status="pending",
        )

        cart.items.all().delete()

        serializer = OrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message": "Purchase created successfully.",
                "order": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class CreatePaymentView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        try:
            cart = Cart.objects.get(
                user=request.user
            )

        except Cart.DoesNotExist:
            raise ValidationError(
                "Cart is empty."
            )

        cart_items = cart.items.select_related(
            "product"
        )

        if not cart_items.exists():
            raise ValidationError(
                "Cart is empty."
            )

        total_price = Decimal("0.00")

        for item in cart_items:

            product = item.product

            if not product:
                raise ValidationError(
                    "Invalid product."
                )

            if not product.is_active:
                raise ValidationError(
                    f"{product.name} is unavailable."
                )

            total_price += (
                product.price * item.quantity
            )

        discount_amount = Decimal("0.00")

        final_price = (
            total_price - discount_amount
        )

        order = Order.objects.create(
            user=request.user,
            payment_method="online",
            payment_status="pending",
            status="pending",
            total_price=total_price,
            discount_amount=discount_amount,
            final_price=final_price,
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        OrderStatusHistory.objects.create(
            order=order,
            status="pending",
        )

        try:

            razorpay_order = create_razorpay_order(
                final_price
            )

        except Exception as e:

            order.delete()

            raise ValidationError(
                str(e)
            )

        order.razorpay_order_id = razorpay_order["id"]

        order.save(
            update_fields=[
                "razorpay_order_id",
            ]
        )

        return Response(
            {
                "message": "Razorpay order created successfully.",

                "order_id": order.order_id,

                "razorpay_order_id": razorpay_order["id"],

                "amount": razorpay_order["amount"],

                "currency": razorpay_order["currency"],

                "key": settings.RAZORPAY_KEY_ID,

                "user": {
                    "name": request.user.get_full_name(),
                    "email": request.user.email,
                    "contact": request.user.phone,
                },

            },
            status=status.HTTP_200_OK,
        )


class VerifyPaymentView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        order_id = request.data.get("order_id")

        razorpay_order_id = request.data.get(
            "razorpay_order_id"
        )

        razorpay_payment_id = request.data.get(
            "razorpay_payment_id"
        )

        razorpay_signature = request.data.get(
            "razorpay_signature"
        )

        if (
            not order_id
            or not razorpay_order_id
            or not razorpay_payment_id
            or not razorpay_signature
        ):
            raise ValidationError(
                "Missing payment details."
            )

        try:

            order = Order.objects.get(
                order_id=order_id,
                user=request.user,
                razorpay_order_id=razorpay_order_id,
            )

        except Order.DoesNotExist:

            raise NotFound(
                "Order not found."
            )

        if order.payment_status == "paid":

            return Response(
                {
                    "message": "Payment already verified."
                },
                status=status.HTTP_200_OK,
            )

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET,
            )
        )

        try:

            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                }
            )

        except razorpay.errors.SignatureVerificationError:

            raise ValidationError(
                "Invalid payment signature."
            )

        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature

        order.payment_status = "paid"
        order.status = "completed"

        order.save(
            update_fields=[
                "razorpay_payment_id",
                "razorpay_signature",
                "payment_status",
                "status",
            ]
        )

        OrderStatusHistory.objects.create(
            order=order,
            status="completed",
        )

        Cart.objects.filter(
            user=request.user
        ).delete()

        serializer = OrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message": "Payment verified successfully.",
                "order": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class MyOrdersView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [
        IsAuthenticated
    ]

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
    permission_classes = [
        IsAuthenticated
    ]

    def get_object(self):

        try:

            return (
                Order.objects
                .prefetch_related(
                    "items",
                    "status_history",
                )
                .get(
                    order_id=self.kwargs[
                        "order_id"
                    ],
                    user=self.request.user,
                )
            )

        except Order.DoesNotExist:
            raise NotFound(
                "Purchase not found."
            )


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):

        try:
            order = Order.objects.get(
                order_id=order_id,
                user=request.user,
            )

        except Order.DoesNotExist:
            raise NotFound(
                "Purchase not found."
            )

        if order.payment_status == "paid":
            raise ValidationError(
                "Paid purchases cannot be cancelled."
            )

        if order.status == "cancelled":
            raise ValidationError(
                "Purchase already cancelled."
            )

        order.status = "cancelled"
        order.save(
            update_fields=["status"]
        )

        OrderStatusHistory.objects.create(
            order=order,
            status="cancelled",
        )

        return Response(
            {
                "message":
                "Purchase cancelled successfully."
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

        status = self.request.query_params.get(
            "status"
        )

        payment_status = (
            self.request.query_params.get(
                "payment_status"
            )
        )

        search = self.request.query_params.get(
            "search"
        )

        if status:
            queryset = queryset.filter(
                status=status
            )

        if payment_status:
            queryset = queryset.filter(
                payment_status=payment_status
            )

        if search:

            queryset = queryset.filter(
                Q(order_id__icontains=search)
                |
                Q(user__username__icontains=search)
                |
                Q(user__email__icontains=search)
            )

        return queryset


class AdminOrderDetailView(
    RetrieveAPIView
):
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
                    order_id=self.kwargs[
                        "order_id"
                    ]
                )
            )

        except Order.DoesNotExist:

            raise NotFound(
                "Purchase not found."
            )


class UpdateOrderStatusView(APIView):

    permission_classes = [IsAdminUser]

    ALLOWED_STATUS = [
        "pending",
        "completed",
        "cancelled",
    ]

    def patch(self, request, order_id):

        try:
            order = Order.objects.get(
                order_id=order_id
            )

        except Order.DoesNotExist:
            raise NotFound(
                "Purchase not found."
            )

        new_status = request.data.get(
            "status"
        )

        if new_status not in self.ALLOWED_STATUS:
            raise ValidationError(
                "Invalid status."
            )

        if order.status == new_status:
            raise ValidationError(
                "Status already updated."
            )

        order.status = new_status

        if new_status == "completed":
            order.payment_status = "paid"

        order.save()

        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
        )

        serializer = OrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "message":
                "Purchase updated successfully.",
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

        return Response(
            {
                "total_products": total_products,
                "total_orders": total_orders,
                "total_users": total_users,
                "total_revenue": revenue,
            }
        )


class DownloadEbookView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, order_item_id):

        try:

            order_item = (
                OrderItem.objects
                .select_related(
                    "order",
                    "product",
                )
                .get(
                    id=order_item_id,
                    order__user=request.user,
                )
            )

        except OrderItem.DoesNotExist:

            raise NotFound(
                "Purchase not found."
            )

        if order_item.order.payment_status != "paid":
            raise ValidationError(
                "Payment is pending."
            )

        if not order_item.product:
            raise ValidationError(
                "Book not found."
            )

        if not order_item.product.ebook_file:
            raise ValidationError(
                "E-book file not available."
            )

        order_item.download_count += 1
        order_item.last_downloaded_at = timezone.now()

        order_item.save(
            update_fields=[
                "download_count",
                "last_downloaded_at",
            ]
        )

        return FileResponse(
            order_item.product.ebook_file.open(
                "rb"
            ),
            as_attachment=True,
            filename=order_item.product.ebook_file.name.split("/")[-1],
        )


class LibraryView(ListAPIView):

    serializer_class = LibrarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return (
            OrderItem.objects
            .select_related(
                "product",
                "order",
            )
            .filter(
                order__user=self.request.user,
                order__payment_status="paid",
            )
            .order_by(
                "-order__created_at"
            )
        )
