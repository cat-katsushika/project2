from django.urls import path

from teams import views

app_name = "teams"
urlpatterns = [
    path("v1/teams/", views.TeamsAPIView.as_view(), name="team-list"),
]
