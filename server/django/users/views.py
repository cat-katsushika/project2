# from django.shortcuts import render

# Create your views here.
from rest_framework import generics

from users.serializers import UserSerializer

from .models import User


# Create your views here.
class SignUpAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
