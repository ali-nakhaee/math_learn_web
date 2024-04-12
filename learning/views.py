""" learning.views file """
import random
from sympy import sympify, symbols

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from .models import Practice, ConstantText, Answer, Help, Question
from users.models import User

sample_user = User.objects.get(username='Ali')

def make_sample_question(base_question_id):
    """ Function to make sample question from base question """
    try:
        base_question = Question.objects.get(id=base_question_id)
    except Question.DoesNotExist:
        raise Exception('Base question does not exist')
    sample_variable = random.randint(base_question.variable_min, base_question.variable_max)
    sample_question_text = base_question.text.replace(base_question.variable, sample_variable)
    expression = base_question.true_answer
    x = symbols(base_question.variable)
    answer_function = sympify(expression)
    sample_question_answer = answer_function.subs(x, sample_variable)



class IndexPage(View):
    def get(self, request):
        return render(request, "learning/index.html")

class AddPractice(View):
    def get(self, request):
        return render(request, 'learning/add_practice.html')
    
    def post(self, request):
        fields = request.POST.keys()
        practice = Practice.objects.create(teacher=sample_user)
        for field in fields:
            field_name = field.split('_')[0]
            if field_name == 'text':
                step = field.split('_')[1]
                text = request.POST.get(field)
                ConstantText.objects.create(practice=practice, text=text, step=step)
            elif field_name == 'answer':
                step = field.split('_')[1]
                true_answer = request.POST.get(field)
                Answer.objects.create(practice=practice, true_answer=true_answer, step=step)
            elif field_name == 'help':
                step = field.split('_')[1]
                text = request.POST.get(field)
                Help.objects.create(practice=practice, text=text, step=step)
                
        return HttpResponse(practice)
