from rest_framework import generics, status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from teams.models import Team,Task
from users.serializers import ChangeUsernameSerializer, MyTokenObtainPairSerializer, UserSerializer
from .models import User


# Create your views here.
@authentication_classes([])
@permission_classes([])
class SignUpAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ObtainTokenPairWithColorView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ChangeUsernameAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeUsernameSerializer

    def put(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            get_new_username = request.data.get("username")

            new_username = get_new_username.strip()
            if not new_username:
                return Response({"error": "ユーザネームを入力してください"}, status=status.HTTP_400_BAD_REQUEST)
            elif user.username == new_username:
                return Response({"error": "新しいユーザネームを登録してください"}, status=status.HTTP_400_BAD_REQUEST)
            elif User.objects.filter(username=new_username).exists():
                return Response({"error": "同じユーザネームが既に存在します"}, status=status.HTTP_400_BAD_REQUEST)
            user.username = new_username
            user.save()
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteAccountsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request):
        user = request.user
        #ログインユーザーが所属しているチームを取得
        teams = user.teams.all()
        for team in teams:
            other_members = team.users.exclude(id=user.id).order_by('id')
            next_user = other_members.first()
            task = Task.objects.filter(user=user, team=team, status=Task.Status.IN_PROGRESS)
            #所属ユーザーがログインユーザーのみの場合，そのチームも削除
            if other_members.count() == 0:
                team.delete()
            #チームメンバーが他にもいる，かつ爆弾を持っているのが退会するユーザである場合は昇順でidが最初の人に爆弾を渡す
            elif task.exists():
                task.delete()
                Task.objects.create(user=next_user, team=team, status=Task.Status.IN_PROGRESS)
        user.delete()
        return Response(status=status.HTTP_200_OK)
    

        
        
        
        
        