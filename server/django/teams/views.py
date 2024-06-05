from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from teams.models import Task, Team
from teams.serializers import JoinedTeamSerializer, TeamCreateSerializer, TeamJoinSerializer, TeamSerializer


class TeamsAPIView(ListAPIView, PageNumberPagination):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class TeamCreateAPIView(CreateAPIView):
    serializer_class = TeamCreateSerializer

    def perform_create(self, serializer):
        serializer.save(users=[self.request.user])


class TeamDetailAPIView(APIView):
    def get(self, request, *args, **kwargs):
        team_id = kwargs["team_id"]
        if not Team.objects.filter(id=team_id).exists():
            return Response({"error": "存在しないチームです"}, status=status.HTTP_400_BAD_REQUEST)
        team = Team.objects.get(id=team_id)

        task = team.tasks.filter(status=Task.Status.IN_PROGRESS).first()

        # taskが存在しない場合はtaskを作成する
        # あたらしくTeamを作って最初にアクセスしたときとかが該当
        if not task:
            task = Task.objects.create(user=request.user, team=team, status=Task.Status.IN_PROGRESS)

        continuation_count = Task.objects.filter(team=team, status=Task.Status.COMPLETED).count()

        response_data = {
            "team": {
                "id": str(team.id),
                "name": team.name,
                "description": team.description,
            },
            "task": {
                "id": str(task.id),
                "user": str(task.user.id),
                "created_at": str(task.created_at),
            },
            "continuation_count": continuation_count,
            "users": [{"id": str(user.id), "username": user.username} for user in team.users.all()],
        }

        return Response(response_data, status=status.HTTP_200_OK)


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

    def get_queryset(self):
        user = self.request.user
        return user.teams.all()
