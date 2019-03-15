import uuid

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
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
        email = kwargs.get('email')
        password = kwargs.get('password')
        mobile_number = kwargs.get('mobile_number')

        user = self.model.objects.filter(email=email).first()
        if user:
            raise ValueError(
                'User with email {email} already exists'.format(email=email))
        user = self.model(
            mobile_number=mobile_number, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
        User model
    """

    id = models.CharField(
        max_length=ID_LENGTH, primary_key=True, default=id_gen, editable=False)

    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
