from xml.dom import ValidationErr
from rest_framework import serializers
from accounts.models import *
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["user_email"] = user.email
        token["user_id"] = user.id

        return token


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
        ]


class OnlyUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "is_med_user",
        ]


class UserChangePasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(
        max_length=255,
        style={"input_type": "password"},
        write_only=True,
    )
    new_password = serializers.CharField(
        max_length=255,
        style={"input_type": "password"},
        write_only=True,
    )
    confirm_password = serializers.CharField(
        max_length=255,
        style={"input_type": "password"},
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            "current_password",
            "new_password",
            "confirm_password",
        ]

    def validate(self, attrs):
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")
        user = self.context.get("user")
        if not user.check_password(current_password):
            raise serializers.ValidationError("Current password is incorrect")
        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords must match")
        user.set_password(new_password)
        user.save()
        return attrs


class SendPasswordEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print("Encoded UID", uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print("Password Reset Token", token)
            # demo link
            link = "http://localhost:3000/api/user/reset/" + uid + "/" + token
            print("Password reset link: ", link)
            # send email code
            return attrs
        else:
            raise ValidationErr("This email is not registered")


class PasswordResetSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(
        max_length=255,
        style={"input_type": "password"},
        write_only=True,
    )
    confirm_password = serializers.CharField(
        max_length=255,
        style={"input_type": "password"},
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            "new_password",
            "confirm_password",
        ]

    def validate(self, attrs):
        try:
            new_password = attrs.get("new_password")
            confirm_password = attrs.get("confirm_password")
            uid = self.context.get("uid")
            token = self.context.get("token")
            if new_password != confirm_password:
                raise serializers.ValidationError("Passwords must match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationErr("Token is not valid or expired")
            user.set_password(new_password)
            user.save()
            return attrs

        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise ValidationErr("Token is not valid or expired")


##### REG USER SERIALIZERS #####


class RegProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegUser
        fields = [
            "id",
            "email",
            "name",
            "is_med_user",
            "date_of_birth",
            "gender",
        ]


class RegUserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
    )

    class Meta:
        model = RegUser
        fields = [
            "email",
            "name",
            "password",
            "is_med_user",
            "confirm_password",
            "date_of_birth",
            "gender",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    # validation
    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError("Passwords must match")

        return attrs

    def create(self, validated_data):
        return RegUser.objects.create_reguser(**validated_data)


##### MED USER SERIALIZERS #####


class MedUserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = MedUser
        fields = [
            "email",
            "password",
            "confirm_password",
            "name",
            "is_med_user",
            "qualification",
            "specialization",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

        is_med_user = serializers.BooleanField(required=True)
        qualification = serializers.CharField(required=True)
        specialization = serializers.CharField(required=True)

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError("Passwords must match")

        return attrs

    def create(self, validated_data):
        print(validated_data)
        return MedUser.objects.create_meduser(**validated_data)


class MedUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedUser
        fields = [
            "id",
            "email",
            "name",
            "is_med_user",
            "qualification",
            "specialization",
        ]
