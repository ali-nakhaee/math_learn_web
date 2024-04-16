""" Defines URL patterns for learning app. """

from django.urls import path
from . import views

app_name = "learning"
urlpatterns = [
    path("", views.IndexPage.as_view(), name="index"),
    path("add_practice/", views.AddPractice.as_view(), name="add_practice"),
    path("questions/", views.QuestionsAPIView.as_view(), name="questions"),
    path("homeworks/", views.HomeWorksAPIView.as_view(), name="homeworks"),
]
