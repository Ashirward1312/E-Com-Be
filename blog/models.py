from django.db import models


class Blog(models.Model):

   title = models.CharField(
      max_length=500,
   )

   content = models.TextField()

   is_active = models.BooleanField(
      default=True,
   )

   created_at = models.DateTimeField(
      auto_now_add=True,
   )

   updated_at = models.DateTimeField(
      auto_now=True,
   )

   def __str__(self):
      return self.title

   class Meta:
      ordering = ["-created_at"]
      verbose_name = "Blog"
      verbose_name_plural = "Blogs"