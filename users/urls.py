"""Defines URL patterns for users"""

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

app_name = 'users'
urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
]