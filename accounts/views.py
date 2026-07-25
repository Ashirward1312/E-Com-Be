from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """
    Register New User
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class ProfileView(APIView):
    """
    Logged-in User Profile
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "profile_image": (
                    user.profile_image.url
                    if user.profile_image
                    else None
                ),
                "first_name": user.first_name,
                "last_name": user.last_name,

                # ✅ Important
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "is_active": user.is_active,

                "date_joined": user.date_joined,
            },
            status=status.HTTP_200_OK,
        )