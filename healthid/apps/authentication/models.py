import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from django.utils.http import int_to_base36

ID_LENGTH = 9


def id_gen() -> str:
    """Generates random string whose length is `ID_LENGTH`"""
    return int_to_base36(uuid.uuid4().int)[:ID_LENGTH]


class UserManager(BaseUserManager):
    def create_user(self, **kwargs):
        """
        Creates and saves a User with the given credentials.
        """
        email = kwargs.get("email")
        password = kwargs.get("password")
        mobile_number = kwargs.get("mobile_number")

        user = self.model.objects.filter(email=email).first()
        if user:
            raise ValueError(
                "User with email {email} already exists".format(email=email)
            )
        user = self.model(
            mobile_number=mobile_number, email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password)
        user.is_superuser = user.is_staff = True
        user.is_active = user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
        User model
    """

    id = models.CharField(
        max_length=ID_LENGTH, primary_key=True, default=id_gen, editable=False
    )

    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    mobile_number = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    secondary_email = models.EmailField(max_length=100, null=True, blank=True)
    secondary_phone_number = models.CharField(
        null=True, blank=True, max_length=100)
    created_at = models.DateField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    role = models.ForeignKey(
        "Role", related_name="role",
        null=True, blank=True,
        on_delete=models.CASCADE
    )
    is_staff = models.BooleanField(default=False)
    profile_image = models.URLField(null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_admin_permission(self, perm, obj=None):
        return self.is_admin

    def has_module_permission(self, app_label):
        return self.is_admin

    def has_super_admin_permission(self, perm, obj=None):
        return self.is_superuser


class Role(models.Model):
    """
        User Role model
    """

    id = models.CharField(
        max_length=ID_LENGTH, primary_key=True, default=id_gen, editable=False
    )
    name = models.CharField(
        max_length=50, help_text="Enter Available Roles", unique=True
    )

    class Meta:
        verbose_name_plural = "Roles"
        ordering = ("name",)

    def __str__(self):
        return self.name
