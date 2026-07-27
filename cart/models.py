from django.db import models
from django.conf import settings
from products.models import Product

# ==============================================================================
# CART MODELS
# ==============================================================================

class Cart(models.Model):
    # OneToOneField ensures each user has only one cart
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} ({self.quantity}) in cart for {self.cart.user.username}"


# ==============================================================================
# ORDER MODELS
# ==============================================================================

# ✅ यह आपका नया और विस्तृत Order मॉडल है
class Order(models.Model):

    STATUS_CHOICES = [
        ('placed', 'Placed'),
        ('confirmed', 'Confirmed'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    # user can be null if the user account is deleted later
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    # Shipping Details are stored directly with the order
    full_name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    # Order Information
    order_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Status Fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price per item at the time of order

    def __str__(self):
        return f"{self.product.name} ({self.quantity}) for Order {self.order.order_id}"

        