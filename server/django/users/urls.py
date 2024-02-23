from django.urls import path

from .views import SignUpAPIView

app_name = "users"
urlpatterns = [
    path("v1/users/create/", SignUpAPIView.as_view(), name="signup"),
]
