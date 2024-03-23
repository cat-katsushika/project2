from rest_framework.serializers import ModelSerializer

from teams.models import Team


class TeamSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "users", "description"]  # JSONにするフィールドを指定


class TeamCreateSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = ["name", "description"]


class TeamJoinSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "users", "description"]
