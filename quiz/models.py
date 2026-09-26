from django.db import models

# Create your models here.
from django.db import models


class Quiz(models.Model):

   category = models.CharField(
      max_length=100,
      blank=True,
      null=True,
   )

   question = models.TextField()

   answer = models.TextField()

   created_at = models.DateTimeField(
      auto_now_add=True,
   )

   updated_at = models.DateTimeField(
      auto_now=True,
   )

   def __str__(self):
      return self.question[:50]

   class Meta:
      ordering = ["-created_at"]
      verbose_name = "Quiz"
      verbose_name_plural = "Quizzes"