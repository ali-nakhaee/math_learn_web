""" learning.views file """

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse


class AddPractice(View):
    def get(self, request):
        return render(request, 'learning/add_practice.html')
    
    def post(self, request):
        return HttpResponse('hi')
