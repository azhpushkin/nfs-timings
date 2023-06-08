from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        user = User(username=User.normalize_username(username), **extra_fields)
        user.password = make_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields['is_superuser'] = True
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    @property
    def is_staff(self):
        return self.is_active and self.is_superuser

    def has_perm(self, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff
