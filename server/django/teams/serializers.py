from rest_framework.serializers import ModelSerializer

from teams.models import Team


class TeamSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "description"]  # JSONにするフィールドを指定


class TeamCreateSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = ["name", "description"]


class JoinedTeamSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "description"]  # JSONにするフィールドを指定
