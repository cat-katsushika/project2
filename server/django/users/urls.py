from django.urls import path
from .views import SignUpAPIView

app_name = "users"
urlpatterns = [
    path('signup/',SignUpAPIView.as_view(), name='signup'),
]
