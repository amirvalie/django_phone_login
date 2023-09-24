from urllib import response
from django.test import TestCase
from django.conf import settings
from ..models import PhoneToken
import datetime



class TestView(TestCase):
    def setUp(self) -> None:
        self.phone_number = '09033285705'
        self.otp = 44883
        self.token_object = PhoneToken.objects.create(
            phone_number = self.phone_number,
        )
    def test_check_create_manual_token(self):
        self.token_object.otp = self.otp
        self.token_object.save()
        self.assertEqual(self.token_object.otp, self.otp)
        self.assertEqual(self.token_object.phone_number, self.phone_number)

    def test_check_auto_self_create_token(self):
        otp = PhoneToken.send_otp(self.token_object)
        self.assertEqual(self.token_object.otp, otp)

    def test_validate_otp_return_true(self):
        self.assertTrue(self.token_object.validate_otp())

    def test_validate_otp_return_false(self):
        self.token_object.otp = self.otp
        valid_time = getattr(settings, 'DURATION_OF_OTP_VALIDATY', 5) + 1
        self.token_object.timestamp = self.token_object.timestamp + datetime.timedelta(minutes=valid_time)
        self.token_object.save()
        self.assertFalse(self.token_object.validate_otp())
