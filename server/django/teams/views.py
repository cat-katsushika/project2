from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from rest_framework import status
from teams.models import Team
from teams.serializers import TeamCreateSerializer, TeamSerializer, TeamJoinSerializer, JoinedTeamSerializer
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
        pk = kwargs["pk"]
        if not self.queryset.filter(pk=pk).exists():
            return Response({"error": "存在しないチームです"}, status=status.HTTP_400_BAD_REQUEST)
        team = self.queryset.get(pk=pk)
        if request.user in team.users.all():
            return Response({"error": "既に参加しています"}, status=status.HTTP_400_BAD_REQUEST)
        team.users.add(request.user)
        team.save()
        serializer = self.serializer_class(team)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JoinedTeamsAPIView(ListAPIView, PageNumberPagination):
    serializer_class = JoinedTeamSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return user.joined_teams.all()
