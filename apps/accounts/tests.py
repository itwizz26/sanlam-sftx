from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.wallet.models import Account

User = get_user_model()

class AccountRegistrationTests(APITestCase):
    def test_user_registration_auto_provisions_wallet(self):
        """Ensure a user registration automatically creates an Account record."""
        url = '/api/v1/accounts/register/'
        data = {
            "username": "newuser",
            "password": "securepassword123",
            "email": "user@example.com"
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(username="newuser")
        self.assertTrue(Account.objects.filter(user=user).exists())
        self.assertEqual(Account.objects.get(user=user).balance, 0.00)

    def test_login_returns_token(self):
        """Ensure login returns JWT tokens for an existing user."""
        User.objects.create_user(username="loginuser", password="password123")
        url = '/api/v1/accounts/login/'
        data = {"username": "loginuser", "password": "password123"}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_registration_flow(self):
        """Verify registration flow."""
        url = '/api/v1/accounts/register/'
        data = {
            "username": "testuser",
            "password": "Password123!",
            "email": "test@example.com"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())
        
        user = User.objects.get(username="testuser")
        self.assertTrue(Account.objects.filter(user=user).exists())