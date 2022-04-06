from uuid import uuid4
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('メールアドレスは必須項目です')
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(_("id"), default=uuid4, primary_key=True)
    email = models.EmailField(
        _("email"),
        max_length=255,
        unique=True,
    )
    username = models.CharField(_("username"), default="Anonymous", max_length=16)
    is_staff = models.BooleanField(_("staff"), default=False)
    is_active = models.BooleanField(_("active"), default=False)
    is_superuser = models.BooleanField(_("superuser"), default=False)
    created_at = models.DateTimeField(_("created date"), default=timezone.now)
    updated_at = models.DateTimeField(_("updated date"), auto_now=True)
    last_login = models.DateTimeField(_("last login date"), null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['-created_at']

    def __str__(self):
        return self.email

