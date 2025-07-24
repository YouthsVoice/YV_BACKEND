from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission
)
from django.db import models


class DonorManager(BaseUserManager):
    def create_user(self, email, name, phone, address, password=None):
        if not email:
            raise ValueError("Donors must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, phone=phone, address=address)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, address, password):
        user = self.create_user(email, name, phone, address, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Donor(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    google_sheet_id = models.CharField(max_length=200, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Fix reverse accessor clashes
    groups = models.ManyToManyField(
        Group,
        related_name='donor_users',
        blank=True,
        help_text='The groups this donor belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='donor_user_permissions',
        blank=True,
        help_text='Specific permissions for this donor.',
        verbose_name='user permissions'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone', 'address']

    objects = DonorManager()

    def __str__(self):
        return self.email