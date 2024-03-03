from rest_framework import status
from rest_framework.test import APIClient

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

    def test_login_failure(self):
        data = {"username": "notexistinguser", "password": "notexistingtestpassword"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("No active account found with the given credentials", str(response.data))
