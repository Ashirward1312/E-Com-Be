from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAdminUser

from .models import Blog
from .serializers import BlogSerializer


class BlogListCreateView(generics.ListCreateAPIView):

   serializer_class = BlogSerializer

   parser_classes = [
      MultiPartParser,
      FormParser,
   ]

   filter_backends = [
      SearchFilter,
      OrderingFilter,
   ]

   search_fields = [
      "title",
      "content",
   ]

   ordering_fields = [
      "created_at",
      "title",
   ]

   ordering = [
      "-created_at",
   ]

   def get_queryset(self):

      if self.request.method == "POST":
         return Blog.objects.all()

      return Blog.objects.filter(
         is_active=True
      )

   def get_permissions(self):

      if self.request.method == "POST":
         return [IsAdminUser()]

      return [AllowAny()]


class BlogDetailView(generics.RetrieveUpdateDestroyAPIView):

   serializer_class = BlogSerializer
   lookup_field = "slug"

   parser_classes = [
      MultiPartParser,
      FormParser,
   ]

   def get_queryset(self):

      if self.request.method in [
         "PUT",
         "PATCH",
         "DELETE",
      ]:
         return Blog.objects.all()

      return Blog.objects.filter(
         is_active=True
      )

   def get_permissions(self):

      if self.request.method in [
         "PUT",
         "PATCH",
         "DELETE",
      ]:
         return [IsAdminUser()]

      return [AllowAny()]