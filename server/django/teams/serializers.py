from rest_framework.serializers import ModelSerializer
from teams.models import Team


class TeamSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"

    # JSONにするフィールドを指定
