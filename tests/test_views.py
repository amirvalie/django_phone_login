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
        self.user = User(phone=self.phone_number)
        self.user.set_password('test')
        self.user.save()

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

    def test_login_with_password_valid_response(self):
        session = self.client.session
        session['phone_number'] = self.user.phone
        session.save()
        response = self.client.post(reverse('phone_login:password_login'), {'password': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_login_with_password_invalid_password(self):
        #invalid password
        session = self.client.session
        session['phone_number'] = self.user.phone
        session.save()
        response = self.client.post(reverse('phone_login:password_login'), {'password': 'some_worong_password'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            'form',
            'password',
            'Please enter a correct username and password. Note that both fields may be case-sensitive.'
        )

    def teset_login_with_password_invalid_session(self):
        # not setting phone number to session
        response = self.client.post(reverse('phone_login:password_login'), {'password': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('phone_login:login'))