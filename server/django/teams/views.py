from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from rest_framework import status
from teams.models import Team
from teams.serializers import TeamCreateSerializer, TeamSerializer, TeamJoinSerializer
from rest_framework.response import Response


class TeamsAPIView(ListAPIView, PageNumberPagination):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class TeamCreateAPIView(CreateAPIView):
    serializer_class = TeamCreateSerializer


class TeamJoinAPIView(APIView):
    queryset = Team.objects.all()
    serializer_class = TeamJoinSerializer

    def put(self, request, *args, **kwargs):
        team = self.queryset.get(pk=kwargs["pk"])
        team.users.add(request.user)
        team.save()
        serializer = self.serializer_class(team)
        return Response(serializer.data, status=status.HTTP_200_OK)
