from django.conf import settings
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.core.cache import cache
from .. import views
from django.contrib.auth import get_user_model

User = get_user_model()

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.phone_number = '09033333333'
    def test_generate_token_view_valid_response(self):
        cache.set('127.0.0.1', 0)
        get_response = self.client.get(reverse('phone_login:login'))
        post_response = self.client.post(reverse('phone_login:login'), {'phone_number': self.phone_number})
        self.assertEqual(post_response.status_code, 302)
        self.assertTemplateUsed(get_response, 'registration/generate_token.html')
        self.assertEqual(post_response.url, reverse('phone_login:confirm_otp'))

    def test_generate_token_view_invalid_response(self):
        max_attempts = getattr(settings, 'PHONE_LOGIN_ATTEMPTS', 10)
        response = self.client.post(reverse('phone_login:login'), {'phone_number': self.phone_number})
        for i in range(10):
            response = self.client.post(reverse('phone_login:login'), {'phone_number': self.phone_number})
        get_response = self.client.get(reverse('phone_login:login'))
        self.assertTemplateUsed(get_response, 'registration/invalid_attempts.html')

    def test_generate_token_view_session(self):
        cache.set('127.0.0.1', 0)
        response = self.client.post(
            reverse('phone_login:login'),
            {'phone_number': self.phone_number}
        )
        self.assertEqual(
            self.client.session.get('phone_number'),
            self.phone_number
        )

