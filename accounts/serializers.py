# from rest_framework import serializers
# from .models import User


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = [
#             "username",
#             "email",
#             "phone",
#             "password",
#         ]

#     def validate_email(self, value):
#         value = value.lower()

#         if User.objects.filter(email__iexact=value).exists():
#             raise serializers.ValidationError(
#                 "Email already exists."
#             )
#         return value

#     def validate_username(self, value):
#         if User.objects.filter(username__iexact=value).exists():
#             raise serializers.ValidationError(
#                 "Username already exists."
#             )
#         return value

#     def create(self, validated_data):
#         return User.objects.create_user(
#             username=validated_data["username"],
#             email=validated_data["email"].lower(),
#             phone=validated_data.get("phone"),
#             password=validated_data["password"],
#         )


from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "password",
        ]

    def validate_email(self, value):
        value = value.lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"].lower(),
            phone=validated_data.get("phone"),
            password=validated_data["password"],
        )


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "profile_image",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "is_active",
            "date_joined",
        ]


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "profile_image",
        ]
