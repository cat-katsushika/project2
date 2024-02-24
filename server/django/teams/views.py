from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination

from teams.models import Team
from teams.serializers import TeamCreateSerializer, TeamSerializer


class TeamsAPIView(ListAPIView, PageNumberPagination):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class TeamCreateAPIView(CreateAPIView):
    serializer_class = TeamCreateSerializer
