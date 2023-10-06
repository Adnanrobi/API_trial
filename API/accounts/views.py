from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from accounts.serializers import *
from django.contrib.auth import authenticate, login
from accounts.renderers import UserRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(
            data=request.data,
            context={"user": request.user},
        )
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"msg": "Password Changed Successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendPasswordEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"msg": "Password reset link sent. Please check your email"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = PasswordResetSerializer(
            data=request.data, context={"uid": uid, "token": token}
        )
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"msg": "Password reset successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user  # The authenticated user

        if user is not None:
            # Retrieve the password from the request data
            password = request.data.get("password", None)

            if password is None:
                return Response(
                    {"errors": {"password": ["Password field is required"]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate the provided password
            if user.check_password(password):
                user.delete()
                return Response(
                    {"message": "User deleted successfully"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            else:
                return Response(
                    {"errors": {"non_field_errors": ["Password is incorrect"]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"errors": {"non_field_errors": ["User not found"]}},
                status=status.HTTP_404_NOT_FOUND,
            )


##### REG USER VIEWS #####


class RegUserRegistrationView(APIView):
    def post(self, request, format=None):
        data = request.data.copy()
        data["is_med_user"] = False

        serializer = RegUserRegistrationSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(
                {"msg": "Registration Successful"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegUserLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            password = serializer.data.get("password")
            user_exists = RegUser.objects.filter(email=email).exists()

            if user_exists:
                user = authenticate(request, email=email, password=password)

                if user is not None:
                    # Log the user in
                    login(request, user)

                    # Generate and return an access token
                    access_token = str(AccessToken.for_user(user))
                    return Response(
                        {
                            "msg": "Login Successful",
                            "token": access_token,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "errors": {"password": "Password is not correct."},
                        },
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            else:
                return Response(
                    {"message": "User ID does not exist with this email."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = OnlyUserProfileSerializer(request.user)
        user_id = serializer["id"].value
        try:
            # Query the RegUser table using the user's ID
            reg_user = RegUser.objects.get(id=user_id)

            # Serialize the RegUser data
            serializer = RegProfileSerializer(reg_user)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except RegUser.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )


##### MED USER VIEWS #####


# class MedUserRegistrationView(APIView):
#     def post(self, request, format=None):
#         data = request.data.copy()
#         data["is_med_user"] = True

#         serializer = MedUserRegistrationSerializer(data=data)
#         if serializer.is_valid(raise_exception=True):
#             user = serializer.save()
#             return Response(
#                 {"msg": "Registration Successful"},
#                 status=status.HTTP_201_CREATED,
#             )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MedUserLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            password = serializer.data.get("password")

            # Check if the user ID exists in the table
            user_exists = MedUser.objects.filter(email=email).exists()

            if user_exists:
                user = authenticate(request, email=email, password=password)

                if user is not None:
                    # Log the user in
                    login(request, user)

                    # Generate and return an access token
                    access_token = str(AccessToken.for_user(user))
                    return Response(
                        {
                            "msg": "Login Successful",
                            "token": access_token,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"errors": {"password": "Password is not correct."}},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            else:
                return Response(
                    {"message": "Medical User ID does not exist with this email."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MedProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = OnlyUserProfileSerializer(request.user)
        user_id = serializer["id"].value
        try:
            # Query the MedUser table using the user's ID
            med_user = MedUser.objects.get(id=user_id)

            # Serialize the MedUser data
            serializer = MedUserProfileSerializer(med_user)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except MedUser.DoesNotExist:
            return Response(
                {"detail": "MedUser not found."}, status=status.HTTP_404_NOT_FOUND
            )
