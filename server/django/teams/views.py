from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination

from teams.models import Team
from teams.serializers import TeamCreateSerializer, TeamSerializer, TeamJoinSerializer


class TeamsAPIView(ListAPIView, PageNumberPagination):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class TeamCreateAPIView(CreateAPIView):
    serializer_class = TeamCreateSerializer


class TeamJoinAPIView(CreateAPIView):
    serializer_class = TeamJoinSerializer
    lookup_field = None
    lookup_url_kwarg = "id"
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
