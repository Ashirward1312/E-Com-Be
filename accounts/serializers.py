from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

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