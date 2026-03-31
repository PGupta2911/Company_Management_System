from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role="EMPLOYEE", full_name="", username=None):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            role=role,
            full_name=full_name,
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password,
            role="SUPERADMIN",
            full_name="Super Admin"
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ("SUPERADMIN", "Super Admin"),
        ("HR", "HR"),
        ("EMPLOYEE", "EMPLOYEE"),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="EMPLOYEE")

    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email