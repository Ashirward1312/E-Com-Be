from django.db import models
from django.utils.text import slugify


class Blog(models.Model):

   title = models.CharField(
      max_length=255,
   )

   slug = models.SlugField(
      unique=True,
      blank=True,
   )

   image = models.ImageField(
      upload_to="blogs/",
   )

   content = models.TextField()

   meta_title = models.CharField(
      max_length=255,
      blank=True,
   )

   meta_description = models.TextField(
      blank=True,
   )

   meta_keywords = models.CharField(
      max_length=500,
      blank=True,
   )

   is_active = models.BooleanField(
      default=True,
   )

   created_at = models.DateTimeField(
      auto_now_add=True,
   )

   updated_at = models.DateTimeField(
      auto_now=True,
   )

   def save(self, *args, **kwargs):

      if not self.slug:
         self.slug = slugify(self.title)

      super().save(*args, **kwargs)

   def __str__(self):
      return self.title

   class Meta:
      ordering = ["-created_at"]
      verbose_name = "Blog"
      verbose_name_plural = "Blogs"