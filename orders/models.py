import uuid

from django.conf import settings
from django.db import models

from products.models import Product


class Order(models.Model):

      STATUS_CHOICES = [
         ("placed", "Placed"),
         ("confirmed", "Confirmed"),
         ("packed", "Packed"),
         ("shipped", "Shipped"),
         ("delivered", "Delivered"),
         ("cancelled", "Cancelled"),
      ]

      PAYMENT_METHODS = [
         ("cod", "Cash On Delivery"),
         ("online", "Online Payment"),
      ]

      PAYMENT_STATUS = [
         ("pending", "Pending"),
         ("paid", "Paid"),
         ("failed", "Failed"),
         ("refunded", "Refunded"),
      ]

      user = models.ForeignKey(
         settings.AUTH_USER_MODEL,
         on_delete=models.SET_NULL,
         null=True,
         related_name="orders",
      )

      order_id = models.CharField(
         max_length=20,
         unique=True,
         editable=False,
      )

   # Shipping Details
      full_name = models.CharField(max_length=200)
      phone = models.CharField(max_length=20)
      email = models.EmailField()

      address = models.TextField()
      city = models.CharField(max_length=100)
      state = models.CharField(max_length=100)
      pincode = models.CharField(max_length=10)

    # Amounts
      total_price = models.DecimalField(max_digits=10, decimal_places=2)
      discount_amount = models.DecimalField(
         max_digits=10,
         decimal_places=2,
         default=0,
      )
      final_price = models.DecimalField(max_digits=10, decimal_places=2)

      payment_method = models.CharField(
         max_length=20,
         choices=PAYMENT_METHODS,
         default="cod",
      )

      payment_status = models.CharField(
         max_length=20,
         choices=PAYMENT_STATUS,
         default="pending",
      )

      status = models.CharField(
         max_length=20,
         choices=STATUS_CHOICES,
         default="placed",
      )

      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)

      def save(self, *args, **kwargs):
         if not self.order_id:
               self.order_id = "ORD" + uuid.uuid4().hex[:10].upper()

         super().save(*args, **kwargs)

      def __str__(self):
         return self.order_id


class OrderItem(models.Model):

      order = models.ForeignKey(
         Order,
         on_delete=models.CASCADE,
         related_name="items",
      )

      product = models.ForeignKey(
         Product,
         on_delete=models.SET_NULL,
         null=True,
      )

      quantity = models.PositiveIntegerField()

      price = models.DecimalField(
         max_digits=10,
         decimal_places=2,
      )

      def __str__(self):
         return f"{self.order.order_id} - {self.product}"


class OrderStatusHistory(models.Model):

      order = models.ForeignKey(
         Order,
         on_delete=models.CASCADE,
         related_name="status_history",
      )

      status = models.CharField(
         max_length=20,
         choices=Order.STATUS_CHOICES,
      )

      created_at = models.DateTimeField(
         auto_now_add=True,
      )

      class Meta:
         ordering = ["created_at"]

      def __str__(self):
         return f"{self.order.order_id} - {self.status}"
