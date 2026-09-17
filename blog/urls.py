from django.urls import path

from .views import (
    BlogView,
    BlogDetailView,
)


urlpatterns = [

    path(
        "",
        BlogView.as_view(),
    ),

    path(
        "<int:pk>/",
        BlogDetailView.as_view(),
    ),

]
