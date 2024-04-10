import uuid

from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from django.urls import reverse
from teams.models import Team
from users.models import User

# from rest_framework_simplejwt.serializers import TokenObtainSerializer


class TeamCreateAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.teamcreate_url = reverse("teams:team-create")

    def test_teamcreate_success(self):
        data = {
            "name": "testteam",
            "description": "testteam description",
        }
        response = self.client.post(self.teamcreate_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, data)

    def test_teamcreate_with_empty_name(self):
        data = {
            "name": "",
            "description": "emptyname_team description",
        }
        response = self.client.post(self.teamcreate_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field may not be blank.", response.data["name"])

    def test_teamcreate_with_empty_description(self):
        data = {
            "name": "testteam",
            "description": "",
        }
        response = self.client.post(self.teamcreate_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field may not be blank.", response.data["description"])

    def test_teamcreate_with_duplicated_name(self):
        Team.objects.create(name="testteam", description="testteam description")
        data = {"name": "testteam", "description": "duplicated team description"}

        response = self.client.post(self.teamcreate_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"name": ["team with this name already exists."]})


class TeamJoinAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.team = Team.objects.create(name="testteam", description="testteam description")
        self.teamjoin_url = reverse("teams:team-join", kwargs={"pk": self.team.id})

    def test_teamjoin_success(self):
        response = self.client.put(self.teamjoin_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["users"], [self.user.id])

    def test_teamjoin_with_invalid_team_id(self):
        invalid_uuid = uuid.uuid4()
        invalid_teamjoin_url = reverse("teams:team-join", kwargs={"pk": invalid_uuid})
        response = self.client.put(invalid_teamjoin_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "存在しないチームです"})

    def test_teamjoin_with_already_joined_team(self):
        self.team.users.add(self.user)
        response = self.client.put(self.teamjoin_url, format="json")
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
        self.joinedteams_url = reverse("teams:joined-team-list")

    def test_joinedteams_success(self):
        response = self.client.get(self.joinedteams_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
