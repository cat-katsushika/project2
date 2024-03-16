from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path

from .views import ChangeUsernameAPIView, SignUpAPIView

app_name = "users"
urlpatterns = [
    path("v1/users/create/", SignUpAPIView.as_view(), name="signup"),
    path("v1/users/login/", TokenObtainPairView.as_view(), name="login"),
    path("v1/users/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("v1/users/change_name/", ChangeUsernameAPIView.as_view(), name="change-username"),
]
