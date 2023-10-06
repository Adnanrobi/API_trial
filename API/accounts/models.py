from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        # Creates and saves a User with the given email, name, date_of_birth, gender, and password.
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_reguser(
        self,
        email,
        name,
        password=None,
        is_med_user=None,
        date_of_birth=None,
        gender=None,
        **extra_fields
    ):
        # Creates and saves a User with the given email, name, date_of_birth, gender, and password.
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            is_med_user=is_med_user,
            date_of_birth=date_of_birth,
            gender=gender,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_meduser(
        self,
        email,
        name,
        password,
        is_med_user=None,
        qualification=None,
        specialization=None,
        **extra_fields
    ):
        # Creates and saves a User with the given email, name, date_of_birth, gender, and password.
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            is_med_user=is_med_user,
            qualification=qualification,
            specialization=specialization,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    # def create_user(self, email, password=None, **extra_fields):
    #     if not email:
    #         raise ValueError("The email field must be set")
    #     user = self.model(email=email, **extra_fields)
    #     user.set_password(password)
    #     user.save(using=self._db)
    #     return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        # Creates and saves a superuser with the given email, name, date_of_birth, gender, and password.
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200)
    is_med_user = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "is_med_user"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class RegUser(User):
    date_of_birth = models.DateField(null=True, blank=True)  # Add date_of_birth field
    gender = models.CharField(
        max_length=1,
        choices=(
            ("M", "Male"),
            ("F", "Female"),
            ("O", "Other"),
        ),
        null=True,
        blank=True,
    )


class MedUser(User):
    # Add additional fields specific to MedUser

    qualification = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200)

    # user = models.OneToOneField(
    #     User,
    #     on_delete=models.CASCADE,  # Define the appropriate on_delete behavior
    #     related_name="extended_model",  # Optional: specify a related name
    # )
