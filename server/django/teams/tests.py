import uuid
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from django.urls import reverse
from django.utils import timezone
from teams.models import Task, Team
from users.models import User

# from rest_framework_simplejwt.serializers import TokenObtainSerializer


class TeamCreateAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.team_create_url = reverse("teams:team-create")

    def test_team_create_success(self):
        data = {
            "name": "test team",
            "description": "test team description",
        }
        response = self.client.post(self.team_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, data)
        team = Team.objects.get(name="test team")
        self.assertEqual(team.users.get(username="testuser"), self.user)

    def test_team_create_with_empty_name(self):
        data = {
            "name": "",
            "description": "empty_name_team description",
        }
        response = self.client.post(self.team_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field may not be blank.", response.data["name"])

    def test_team_create_with_empty_description(self):
        data = {
            "name": "test team",
            "description": "",
        }
        response = self.client.post(self.team_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field may not be blank.", response.data["description"])

    def test_team_create_with_duplicated_name(self):
        Team.objects.create(name="test team", description="test team description")
        data = {"name": "test team", "description": "duplicated team description"}

        response = self.client.post(self.team_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"name": ["team with this name already exists."]})


class TeamDetailAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.team = Team.objects.create(name="test team", description="test team description")
        self.team.users.add(self.user)
        self.team_detail_url = reverse("teams:team-detail", kwargs={"team_id": self.team.id})

    def test_team_detail_success(self):
        response = self.client.get(self.team_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["team"]["name"], self.team.name)
        self.assertEqual(response.data["team"]["description"], self.team.description)
        self.assertEqual(response.data["task"]["user"], str(self.user.username))
        self.assertEqual(response.data["continuation_count"], 0)
        self.assertEqual(response.data["users"], [{"id": str(self.user.id), "username": self.user.username}])

    def test_team_detail_with_invalid_team_id(self):
        invalid_uuid = uuid.uuid4()
        invalid_team_detail_url = reverse("teams:team-detail", kwargs={"team_id": invalid_uuid})
        response = self.client.get(invalid_team_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "存在しないチームです"})

    def test_team_detail_with_no_task(self):
        self.team.tasks.all().delete()
        response = self.client.get(self.team_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["task"], None)

    def test_team_detail_with_completed_task(self):
        self.team.tasks.create(user=self.user, status="completed")
        response = self.client.get(self.team_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["continuation_count"], 1)


class TaskDoneAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.team = Team.objects.create(name="test team", description="test team description")
        self.team.users.add(self.user)
        self.team_done_url = reverse("teams:team-done", kwargs={"team_id": self.team.id})

    def test_task_done_success(self):
        self.team.tasks.create(user=self.user, status=Task.Status.IN_PROGRESS)
        response = self.client.post(self.team_done_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "タスクを完了しました"})
        self.assertEqual(self.team.tasks.filter(status=Task.Status.COMPLETED).count(), 1)
        self.assertEqual(self.team.tasks.filter(status=Task.Status.IN_PROGRESS).count(), 1)

    def test_task_done_with_no_task(self):
        response = self.client.post(self.team_done_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "タスクが存在しません"})
        self.assertEqual(self.team.tasks.filter(status=Task.Status.COMPLETED).count(), 0)

    def test_task_done_with_another_user_task(self):
        another_user = User.objects.create_user(username="anotheruser", password="anotherpassword")
        self.team.tasks.create(user=another_user, status=Task.Status.IN_PROGRESS)
        response = self.client.post(self.team_done_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "他のユーザーのタスクは完了できません"})
        self.assertEqual(self.team.tasks.filter(status=Task.Status.COMPLETED).count(), 0)

    def test_task_done_with_task_done_after_24_hours(self):
        native_past_date = datetime.now() - timedelta(days=2)
        aware_past_date = timezone.make_aware(native_past_date)
        task = Task.objects.create(
            user=self.user, team=self.team, status=Task.Status.IN_PROGRESS, created_at=aware_past_date
        )
        task.save()
        response = self.client.post(self.team_done_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "チームは解散しました"})
        self.assertEqual(Team.objects.filter(id=self.team.id).count(), 0)


class TeamJoinAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.team = Team.objects.create(name="test team", description="test team description")
        self.team_join_url = reverse("teams:team-join", kwargs={"pk": self.team.id})

    def test_team_join_success(self):
        response = self.client.put(self.team_join_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["users"], [self.user.id])

    def test_team_join_with_invalid_team_id(self):
        invalid_uuid = uuid.uuid4()
        invalid_team_join_url = reverse("teams:team-join", kwargs={"pk": invalid_uuid})
        response = self.client.put(invalid_team_join_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "存在しないチームです"})

    def test_team_join_with_already_joined_team(self):
        self.team.users.add(self.user)
        response = self.client.put(self.team_join_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "既に参加しています"})


class JoinedTeamsAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.team = Team.objects.create(name="testteam", description="testteam description")
        self.team.users.add(self.user)
        self.joined_teams_url = reverse("teams:joined-team-list")

    def test_joined_teams_success(self):
        response = self.client.get(self.joined_teams_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
