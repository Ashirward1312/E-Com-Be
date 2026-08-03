# from django.db import models
# from django.conf import settings
# from django.utils.text import slugify


# class Category(models.Model):
#     name = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name


# class Product(models.Model):
#     category = models.ForeignKey(
#         Category, on_delete=models.CASCADE, related_name="products"
#     )
#     name = models.CharField(max_length=200)
#     slug = models.SlugField(unique=True, blank=True)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     stock = models.PositiveIntegerField(default=0)
#     image = models.ImageField(upload_to="products/", blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
#     )

#     def save(self, *args, **kwargs):

#         if not self.slug:

#             base_slug = slugify(self.name)
#             slug = base_slug
#             count = 1

#             while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
#                 slug = f"{base_slug}-{count}"
#                 count += 1

#             self.slug = slug

#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.name


# class ProductImage(models.Model):
#     product = models.ForeignKey(
#         Product, on_delete=models.CASCADE, related_name="images"
#     )

#     image = models.ImageField(upload_to="products/")

#     def __str__(self):
#         return f"Image for {self.product.name}"


# class Coupon(models.Model):
#     code = models.CharField(max_length=20, unique=True)
#     discount_percentage = models.IntegerField()
#     active = models.BooleanField(default=True)

#     def __str__(self):
#         return self.code


from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )

    name = models.CharField(max_length=200)

    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    author = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    # Remove later after digital flow is complete
    stock = models.PositiveIntegerField(default=0)

    pages = models.PositiveIntegerField(default=0)

    language = models.CharField(
        max_length=50,
        default="English",
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
    )

    ebook_file = models.FileField(
        upload_to="ebooks/",
        blank=True,
        null=True
    )

    preview_file = models.FileField(
        upload_to="previews/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1

            while Product.objects.filter(
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="products/",
    )

    def __str__(self):
        return f"Image for {self.product.name}"


class Coupon(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True,
    )

    discount_percentage = models.IntegerField()

    active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.code
