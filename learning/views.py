""" learning.views file """

from django.shortcuts import render
from django.views import View


class AddPractice(View):
    """ View for adding practice. """
    def get(self, request):
        return render(request, 'learning/add_practice.html')
