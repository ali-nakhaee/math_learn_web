""" learning.views file """
import random
import time
from sympy import sympify, symbols

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated

from .models import Practice, ConstantText, Answer, Help, Question, HomeWork
from .serializers import QuestionSerializer, HomeWorkSerializer


def make_sample_question(base_question_id):
    """ Function to make sample question from base question """
    # should add as a method to a view
    
    base_question = Question.objects.get(id=base_question_id)
    sample_variable = random.randint(base_question.variable_min, base_question.variable_max)
    sample_question_text = base_question.text.replace(base_question.variable, str(sample_variable))
    expression = base_question.true_answer
    x = symbols(base_question.variable)
    answer_function = sympify(expression)
    sample_question_answer = float(answer_function.subs(x, sample_variable))
    print(sample_question_text)
    print(type(sample_question_answer))
    print(sample_question_answer)
    return None



class IndexPage(View):
    def get(self, request):
        return render(request, "learning/index.html")


class AddPractice(View):
    def get(self, request):
        return render(request, 'learning/add_practice.html')
    
    def post(self, request):
        fields = request.POST.keys()
        practice = Practice.objects.create(teacher=request.user)
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


class QuestionsAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        questions = Question.objects.filter(teacher=request.user).order_by('-date_created')
        questions_serializer = QuestionSerializer(questions, many=True)
        return Response(questions_serializer.data, status.HTTP_200_OK)

    def post(self, request: Request):
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=request.user)
            return Response("Question created.", status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class EditQuestionAPIView(APIView):
    # get, put, delete
    pass


class HomeWorksAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        start = time.time() * 1000
        homeworks = HomeWork.objects.filter(teacher=request.user).order_by('-date_created').prefetch_related('questions')
        serializer = HomeWorkSerializer(homeworks, many=True)
        data = serializer.data
        print("duration:", time.time() * 1000 - start)
        return Response(data, status.HTTP_200_OK)
    
    def post(self, request: Request):
        serializer = HomeWorkSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response("HomeWork created.", status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
       