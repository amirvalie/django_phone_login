import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
import pytz
from django_phone_login.models import PhoneToken
from django.utils import timezone

User=get_user_model()

class PhoneBackend(ModelBackend):

    def get_or_create_user(self,phone_number):
        try:
            return User.objects.get(phone=phone_number)
        except User.DoesNotExist:
            print('user does not exist')
            return User.objects.create(
                phone=phone_number,
                is_active=True
            )
    def authenticate(self,request,otp,phone_number):
        """
        we check the phone number and SMS OTP and the time validity of the SMS OTP.
        If the information is correct, a user will be created or taken with the given phone number
        """
        try:
            expire_time=getattr(settings, 'EXPIRE_TIME', 10)
            diffrence_time=timezone.now() + datetime.timedelta(minutes=expire_time)
            phone_token=PhoneToken.objects.get(
                phone_number=phone_number,
                otp = otp,
                timestamp__lte=diffrence_time,
                used = False
            )
        except PhoneToken.DoesNotExist:
            return None
        user=self.get_or_create_user(phone_number)
        if self.user_can_authenticate(user):
            return user 
        return         

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None