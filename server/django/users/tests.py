from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from django.test import TestCase
from django.urls import reverse

from .models import User
from teams.models import Team,Task

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


class ChangeUsernameAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        User.objects.create_user(username="anotheruser", password="anotherpassword")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.url = reverse("users:change_username")

    def test_changeusername_success(self):
        data = {"username": "newtestuser"}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_changeusername_sameusername(self):
        data = {"username": "testuser"}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("新しいユーザネームを登録してください", response.data["error"])

    def test_changeusername_emptyfield(self):
        data = {"username": ""}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ユーザネームを入力してください", response.data["error"])

    def test_changeusername_existinguser(self):
        data = {"username": "anotheruser"}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("同じユーザネームが既に存在します", response.data["error"])
        
class DeleteAccountsAPITest(APITestCase):
    def setUp(self):
        #ユーザ－関連
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.user2 = User.objects.create_user(username="user2", password="anotherpassword")
        self.user3 = User.objects.create_user(username="user3", password="anotherpassword")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.url = reverse("users:delete_accounts")
        #チーム関連
        self.team1 = Team.objects.create(name="test_team", description="test _team_description")
        self.team2 = Team.objects.create(name="test_team2", description="test_team2_description")
        self.team1.users.add(self.user)
        self.team2.users.add(self.user)
        self.team2.users.add(self.user2)
        self.team2.users.add(self.user3)
        #タスク関連
        Task.objects.create(user=self.user, team=self.team2, status=Task.Status.IN_PROGRESS)
    def test_delete_accounts_success(self):
        self.assertEqual(User.objects.all().count(),3)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #総人数が1人減って2人になっていることを確認
        self.assertEqual(User.objects.all().count(),2)
    def test_delete_teams_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #チーム1は削除され，チーム2は残ることを確認
        self.assertFalse(Team.objects.filter(id=self.team1.id).exists())
        self.assertTrue(Team.objects.filter(id=self.team2.id).exists())
    def test_change_tasks_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #self.userの爆弾(タスク)をuser2またはuser3に渡す
        self.assertFalse(Task.objects.filter(user=self.user, team=self.team2, status=Task.Status.IN_PROGRESS).exists())
        self.assertTrue(Task.objects.filter(user__in=[self.user2, self.user3], team=self.team2, status=Task.Status.IN_PROGRESS).exists())
        
