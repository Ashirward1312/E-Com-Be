# from rest_framework import generics
# from rest_framework.filters import SearchFilter, OrderingFilter
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.permissions import AllowAny, IsAdminUser

# from .models import Blog
# from .serializers import BlogSerializer


# class BlogListCreateView(generics.ListCreateAPIView):

#    serializer_class = BlogSerializer

#    parser_classes = [
#       MultiPartParser,
#       FormParser,
#    ]

#    filter_backends = [
#       SearchFilter,
#       OrderingFilter,
#    ]

#    search_fields = [
#       "title",
#       "content",
#    ]

#    ordering_fields = [
#       "created_at",
#       "title",
#    ]

#    ordering = [
#       "-created_at",
#    ]

#    def get_queryset(self):

#       if self.request.method == "POST":
#          return Blog.objects.all()

#       return Blog.objects.filter(
#          is_active=True
#       )

#    def get_permissions(self):

#       if self.request.method == "POST":
#          return [IsAdminUser()]

#       return [AllowAny()]


# class BlogDetailView(generics.RetrieveUpdateDestroyAPIView):

#    serializer_class = BlogSerializer

#    parser_classes = [
#       MultiPartParser,
#       FormParser,
#    ]

#    def get_queryset(self):

#       if self.request.method in [
#          "PUT",
#          "PATCH",
#          "DELETE",
#       ]:
#          return Blog.objects.all()

#       return Blog.objects.filter(
#          is_active=True
#       )

#    def get_permissions(self):

#       if self.request.method in [
#          "PUT",
#          "PATCH",
#          "DELETE",
#       ]:
#          return [IsAdminUser()]

#       return [AllowAny()]


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser

from .models import Blog
from .serializers import BlogSerializer


class BlogView(APIView):

   def get(self, request):

      blogs = Blog.objects.filter(
         is_active=True
      )

      serializer = BlogSerializer(
         blogs,
         many=True
      )

      return Response(
         serializer.data,
         status=status.HTTP_200_OK
      )

   def post(self, request):

      if not request.user.is_authenticated or not request.user.is_staff:
         return Response(
            {
               "detail": "Admin access required."
            },
            status=status.HTTP_403_FORBIDDEN
         )

      serializer = BlogSerializer(
         data=request.data
      )

      if serializer.is_valid():

         serializer.save()

         return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
         )

      return Response(
         serializer.errors,
         status=status.HTTP_400_BAD_REQUEST
      )


class BlogDetailView(APIView):

   def get(self, request, pk):

      try:

         blog = Blog.objects.get(
            pk=pk,
            is_active=True
         )

      except Blog.DoesNotExist:

         return Response(
            {
               "detail": "Blog not found."
            },
            status=status.HTTP_404_NOT_FOUND
         )

      serializer = BlogSerializer(blog)

      return Response(
         serializer.data,
         status=status.HTTP_200_OK
      )

   def put(self, request, pk):

      if not request.user.is_authenticated or not request.user.is_staff:
         return Response(
            {
               "detail": "Admin access required."
            },
            status=status.HTTP_403_FORBIDDEN
         )

      try:

         blog = Blog.objects.get(
            pk=pk
         )

      except Blog.DoesNotExist:

         return Response(
            {
               "detail": "Blog not found."
            },
            status=status.HTTP_404_NOT_FOUND
         )

      serializer = BlogSerializer(
         blog,
         data=request.data
      )

      if serializer.is_valid():

         serializer.save()

         return Response(
            serializer.data,
            status=status.HTTP_200_OK
         )

      return Response(
         serializer.errors,
         status=status.HTTP_400_BAD_REQUEST
      )

   def delete(self, request, pk):

      if not request.user.is_authenticated or not request.user.is_staff:
         return Response(
            {
               "detail": "Admin access required."
            },
            status=status.HTTP_403_FORBIDDEN
         )

      try:

         blog = Blog.objects.get(
            pk=pk
         )

      except Blog.DoesNotExist:

         return Response(
            {
               "detail": "Blog not found."
            },
            status=status.HTTP_404_NOT_FOUND
         )

      blog.delete()

      return Response(
         {
            "detail": "Blog deleted successfully."
         },
         status=status.HTTP_204_NO_CONTENT
      )