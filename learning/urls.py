""" Defines URL patterns for learning app. """

from django.urls import path
from . import views

app_name = "learning"
urlpatterns = [
    path("", views.IndexPage.as_view(), name="index"),
    path("add_practice/", views.AddPractice.as_view(), name="add_practice"),
    path("questions/", views.QuestionsAPIView.as_view(), name="questions"),
    path("homeworks/", views.HomeWorksAPIView.as_view(), name="homeworks"),
    path("get_homework/<int:homework_id>/", views.GetHomeWorkAPIView.as_view(), name="get_homework"),
    path("get_key/", views.GetTeacherKeyAPIView.as_view(), name="get_key"),
    path("add_teacher/", views.AddTeacherAPIView.as_view(), name="add_teacher"),
    path("homeworks_list/", views.HomeWorksListAPIView.as_view(), name="homeworks_list"),
    path("homework_evaluation/", views.HomeWorkAnswerEvaluationAPIView.as_view(), name="homework_evaluation"),
]
