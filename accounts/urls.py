from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    UpdateProfileView,
    AdminUserListView,
    AdminUserDetailView,
    UserDashboardView
)

urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="refresh",
    ),
    path(
        "profile/",
        ProfileView.as_view(),
        name="profile",
    ),
    path(
        "profile/update/",
        UpdateProfileView.as_view(),
        name="update-profile",
    ),

    path(
        "admin/users/",
        AdminUserListView.as_view(),
        name="admin-users",
    ),

    path(
        "admin/users/<int:pk>/",
        AdminUserDetailView.as_view(),
        name="admin-user-detail",
    ),
    path(
    "dashboard/",
    UserDashboardView.as_view(),
    name="user-dashboard",
),
]
