from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path

from .views import SignUpAPIView

app_name = "users"
urlpatterns = [
    path("v1/users/create/", SignUpAPIView.as_view(), name="signup"),
    path("v1/users/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("v1/users/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
