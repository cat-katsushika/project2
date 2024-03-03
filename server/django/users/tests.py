from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from .models import User


class SignUpAPItest(TestCase):
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
