from django.db import models
import random
import datetime
from django.conf import settings
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
import pytz
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None):
        if not phone:
            raise ValueError('User must have a phone number')
        user = self.model(phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None):
        """
        Creates and saves a superuser with the given email
        """
        user = self.create_user(
            phone=phone,
            password=password,
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        blank=True,
    )
    email = models.EmailField(
        verbose_name='email field',
        max_length=60,
        unique=True,
        null=True, blank=True,
    )
    phone_regex = RegexValidator(
        regex=r'09(\d{9})$',
        message='Enter a valid mobile number. This value may contain only numbers.',
    )
    phone = models.CharField(
        verbose_name='phone field',
        max_length=11,
        unique=True,
        validators=[phone_regex],
    )

    objects = UserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []


class PhoneToken(models.Model):
    phone_regex = RegexValidator(
        regex=r'09(\d{9})$',
        message='Enter a valid mobile number. This value may contain only numbers.',
    )
    phone_number = models.CharField(
        max_length=11,
        validators=[phone_regex],
    )
    otp = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, editable=False)

    def validate_otp(self):
        """
        This method checks whether it is allowed to send the code or not
        """
        valid_otp = getattr(settings, 'DURATION_OF_OTP_VALIDATY', 5)
        if (self.otp is None
                or timezone.now() > self.timestamp + datetime.timedelta(minutes=valid_otp)):
            return True
        return

    @classmethod
    def send_otp(cls, obj):
        if obj.validate_otp() == True:
            obj.otp = cls.generate_otp()
            obj.save()
            print(obj.otp)
            return obj.otp

    @classmethod
    def generate_otp(cls):
        """
        Generate random number for otp
        """
        number = '0123456789'
        length = 5
        key = "".join(random.sample(number, length))
        return int(key)

    def __str__(self):
        return self.phone_number
