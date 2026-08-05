from django.urls import path

from .views import (
   BlogListCreateView,
   BlogDetailView,
)

urlpatterns = [

   path(
      "",
      BlogListCreateView.as_view(),
   ),

   path(
      "<slug:slug>/",
      BlogDetailView.as_view(),
   ),

]
