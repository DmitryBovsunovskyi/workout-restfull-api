from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a new User
        """
        if not email:
            raise ValueError("Users must have email address!")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        # saving user with options "using=self._db" means that
        # multiple databases can be used in case
        # we use more than 1 database in our project
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a new super user
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email insted of username
    """

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    # by default it is user name but we want to change it to email
    USERNAME_FIELD = "email"

    def __str__(self):

        return self.email
