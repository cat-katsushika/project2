# from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

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
            new_username = request.data.get("username")

            if not new_username:
                return Response({"error": "ユーザネームを入力してください"}, status=status.HTTP_400_BAD_REQUEST)
            elif new_username.isspace() == True:
                return Response({"error": "空白はユーザネームに設定できません"}, status=status.HTTP_400_BAD_REQUEST)
            elif user.username == new_username:
                return Response({"error": "新しいユーザネームを登録してください"}, status=status.HTTP_400_BAD_REQUEST)
            elif User.objects.filter(username=new_username).exists():
                return Response({"error": "同じユーザネームが既に存在します"}, status=status.HTTP_400_BAD_REQUEST)

            user.username = new_username
            user.save()
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
