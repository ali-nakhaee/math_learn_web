from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from .serializers import UserSerializer
from . import forms


class LoginPage(View):
    permission_classes = (AllowAny,)

    def get(self, request):
        form = forms.LoginForm()
        context = {'form': form}
        return render(request, 'registration/login.html', context)

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('learning:index')
            else:
                return Response("Login fialed.")


class LogoutAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        request.user.auth_token.delete()
        return Response(data={'message': f"Bye {request.user.username}!"})
    

class RegisterAPIView(APIView):
    def post(self, request: Request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)