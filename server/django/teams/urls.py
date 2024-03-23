from django.urls import path
from teams import views

app_name = "teams"
urlpatterns = [
    path("v1/teams/", views.TeamsAPIView.as_view(), name="team-list"),
    path("v1/teams/create/", views.TeamCreateAPIView.as_view(), name="team-create"),
    path("v1/teams/join/<int:id>/", views.TeamJoinAPIView.as_view(), name="team-join"),
]
