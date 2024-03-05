from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.test import TestCase
from django.urls import reverse

from .models import User


class SignUpAPITest(TestCase):
    def setUp(self):
        self.signup_url = reverse("users:signup")
        self.client = APIClient()

    def test_signup_success(self):
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(self.signup_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_signup_with_existing_username(self):
        User.objects.create_user(username="existinguser", password="existingpassword")
        data = {"username": "existinguser", "password": "newpassword"}
        response = self.client.post(self.signup_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("A user with that username already exists.", response.data["username"])


class LoginAPITest(TestCase):
    def setUp(self):
        self.login_url = reverse("users:login")
        self.client = APIClient()
        User.objects.create_user(username="testuser", password="testpassword")

    def test_login_success(self):
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_notexistingusername(self):
        data = {"username": "notexistinguser", "password": "testpassword"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("No active account found with the given credentials", response.data["detail"])

    def test_login_incorrectpassword(self):
        data = {"username": "testuser", "password": "incorrectpassword"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("No active account found with the given credentials", response.data["detail"])


class RefreshTokenAPITest(APITestCase):
    def setUp(self):
        self.login_url = reverse("users:login")
        self.refresh_url = reverse("users:token_refresh")
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")

    def get_refresh_token(self, username, password):
        response = self.client.post(self.login_url, {"username": username, "password": password}, format="json")
        return response.data.get("refresh", None)

    def test_refresh_token_success(self):
        refresh_token = self.get_refresh_token("testuser", "testpassword")
        response = self.client.post(self.refresh_url, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_token_failure(self):
        response = self.client.post(self.refresh_url, {"refresh": "invalid_refresh_token"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Token is invalid or expired", response.data["detail"])
        self.assertIn("token_not_valid", response.data["code"])
