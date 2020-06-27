from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
from django.db import models


class UserManger(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user."""
        if not email:
            raise ValueError('The email is required.')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and save a new superuser."""
        user = self.create_user(
            email,
            password=password,
            is_superuser=True,
            is_staff=True,
        )
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email instead of username."""

    USERNAME_FIELD = 'email'

    objects = UserManger()

    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    name = models.CharField(
        max_length=255,
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_staff = models.BooleanField(
        default=False,
    )


class Tag(models.Model):
    """Recipe tags."""

    name = models.CharField(
        max_length=255,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """String representation."""
        return self.name


class Ingredient(models.Model):
    """Recipe ingredient."""

    name = models.CharField(
        max_length=255,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """String representation."""
        return self.name
