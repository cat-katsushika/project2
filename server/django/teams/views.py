from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from teams.models import Team
from teams.serializers import TeamSerializer


class TeamsAPIView(ListAPIView, PageNumberPagination):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
