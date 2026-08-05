from rest_framework import serializers
from .models import Blog


class BlogSerializer(serializers.ModelSerializer):

   image = serializers.SerializerMethodField()

   upload_image = serializers.ImageField(
      source="image",
      write_only=True,
      required=False,
      allow_null=True,
   )

   class Meta:
      model = Blog

      fields = [
         "id",

         "title",
         "slug",

         "image",
         "upload_image",

         "content",

         "meta_title",
         "meta_description",
         "meta_keywords",

         "is_active",

         "created_at",
         "updated_at",
      ]

      read_only_fields = [
         "slug",
         "created_at",
         "updated_at",
      ]

   def get_image(self, obj):

      request = self.context.get("request")

      if obj.image:

         if request:
               return request.build_absolute_uri(
                  obj.image.url
               )

         return obj.image.url

      return None
