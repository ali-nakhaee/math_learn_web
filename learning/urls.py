""" Defines URL patterns for learning app. """

from django.urls import path
from . import views

app_name = "learning"
urlpatterns = [
    path("add_practice/", views.AddPractice.as_view(), name="add_practice"),
]