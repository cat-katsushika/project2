from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination

from teams.models import Team
from teams.serializers import TeamCreateSerializer, TeamSerializer, JoinedTeamSerializer


class TeamsAPIView(ListAPIView, PageNumberPagination):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class TeamCreateAPIView(CreateAPIView):
    serializer_class = TeamCreateSerializer


class JoinedTeamsAPIView(ListAPIView, PageNumberPagination):
    serializer_class = JoinedTeamSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return user.joined_teams.all()
