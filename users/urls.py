"""Defines URL patterns for users"""

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

app_name = 'users'
urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('login_page/', views.LoginPage.as_view(), name='login_page'),
]