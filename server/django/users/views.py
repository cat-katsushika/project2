# from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.serializers import MyTokenObtainPairSerializer, UserSerializer

from .models import User


# Create your views here.
@authentication_classes([])
@permission_classes([])
class SignUpAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ObtainTokenPairWithColorView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RefreshTokenView(TokenRefreshView):
    pass
