from datetime import datetime, timedelta

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
                "user": str(task.user.username),
                "created_at": str(task.created_at),
            },
            "continuation_count": continuation_count,
            "users": [{"id": str(user.id), "username": user.username} for user in team.users.all()],
        }

        return Response(response_data, status=status.HTTP_200_OK)


class TaskDoneAPIView(APIView):
    def post(self, request, *args, **kwargs):
        team_id = kwargs["team_id"]
        if not Team.objects.filter(id=team_id).exists():
            return Response({"error": "存在しないチームです"}, status=status.HTTP_400_BAD_REQUEST)
        team = Team.objects.get(id=team_id)

        task = team.tasks.filter(status=Task.Status.IN_PROGRESS).first()
        if not task:
            return Response({"error": "タスクが存在しません"}, status=status.HTTP_400_BAD_REQUEST)

        if task.user != request.user:
            return Response({"error": "他のユーザーのタスクは完了できません"}, status=status.HTTP_400_BAD_REQUEST)

        # タスクが24時間以内に完了していない場合
        created_at_naive = task.created_at.replace(tzinfo=None)
        if created_at_naive + timedelta(days=1) < datetime.now():
            users = list(team.users.all())
            if len(users) == 1:
                team.delete()
                return Response({"message": "チームは解散しました"}, status=status.HTTP_200_OK)
            # チームに残っているユーザーがいる場合
            request_user_index = users.index(request.user)
            next_user_index = (request_user_index + 1) % len(users)
            next_user = users[next_user_index]
            new_task = Task.objects.create(user=next_user, team=team, status=Task.Status.IN_PROGRESS)
            new_task.save()
            # チームからユーザーを削除して保存
            team.users.remove(request.user)
            team.save()
            task.delete()
            task.save()
            return Response({"error": "タスクは24時間以内に完了してください"}, status=status.HTTP_400_BAD_REQUEST)

        task.status = Task.Status.COMPLETED
        task.save()

        users = list(team.users.all())
        request_user_index = users.index(request.user)
        next_user_index = (request_user_index + 1) % len(users)
        next_user = users[next_user_index]
        new_task = Task.objects.create(user=next_user, team=team, status=Task.Status.IN_PROGRESS)
        new_task.save()

        return Response({"message": "タスクを完了しました"}, status=status.HTTP_200_OK)


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
