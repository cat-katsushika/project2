from rest_framework.views import APIView
from rest_framework.response import Response
from teams.models import Team
from teams.serializers import TeamSerializer


class TeamsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Team.objects.all()
        serializer = TeamSerializer(
            queryset, many=True
        )  # many:基本はひとつずつ入る前提なので、複数入る可能性があるときに書く
        return Response(serializer.data)  # 辞書を返す
