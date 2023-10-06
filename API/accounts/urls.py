from django.urls import path
from accounts.views import *
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    # path("register/", RegUserRegistrationView.as_view(), name="register"),
    path("login/", RegUserLoginView.as_view(), name="login"),
    path("profile/", RegProfileView.as_view(), name="profile"),
    path("change-password/", UserChangePasswordView.as_view(), name="change-password"),
    path(
        "send-reset-password-email/",
        SendPasswordEmailView.as_view(),
        name="send-reset-password-email",
    ),
    path(
        "reset-password/<uid>/<token>/",
        PasswordResetView.as_view(),
        name="reset-password",
    ),
    path("delete/", UserDeleteView.as_view(), name="user-delete"),
    path("med-register/", MedUserRegistrationView.as_view(), name="med-registration"),
    path("med-login/", MedUserLoginView.as_view(), name="med-login"),
    path("med-profile/", MedProfileView.as_view(), name="med-profile"),
]
