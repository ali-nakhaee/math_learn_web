""" learning.views file """
import random
import time
from sympy import sympify, symbols
import pdfkit

from django.utils.crypto import get_random_string
from django.template.loader import get_template
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated

from users.models import User
from .models import Practice, ConstantText, Answer, Help, Question, HomeWork, SampleHomeWork, SampleQuestion, HomeWorkAnswer, QuestionAnswer
from .serializers import QuestionSerializer, HomeWorkSerializer, SampleQuestionSerializer, HomeWorkAnswerSerializer


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
       

class EditHomeWorkAPIView(APIView):
    # get, put, delete
    pass


class HomeWorksListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        homeworks = HomeWork.objects.filter(teacher__students=request.user, is_published=True)
        serializer = HomeWorkSerializer(homeworks, fields=('title', 'id'), many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class GetHomeWorkAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def make_sample_question(self, base_question_id):
        """ Function to make sample question from base question """

        base_question = Question.objects.get(id=base_question_id)
        sample_variable = random.randint(base_question.variable_min, base_question.variable_max)
        sample_question_text = base_question.text.replace(base_question.variable, str(sample_variable))
        expression = base_question.true_answer
        x = symbols(base_question.variable)
        answer_function = sympify(expression)
        sample_question_answer = float(answer_function.subs(x, sample_variable))
        return {"text": sample_question_text, "answer": sample_question_answer}

    def post(self, request: Request, homework_id):
        try:
            base_homework = HomeWork.objects.get(id=homework_id)
        except HomeWork.DoesNotExist:
            return Response({"message": "HomeWork Does not Exist"}, status.HTTP_404_NOT_FOUND)
        # to check the homework is published for student
        allowed_homeworks = HomeWork.objects.filter(teacher__students=request.user, is_published=True)
        if base_homework not in allowed_homeworks:
            return Response({"message": "This homework in not for you."}, status.HTTP_403_FORBIDDEN)

        # to check if sample_homework for student was made in past
        if SampleHomeWork.objects.filter(student=request.user, base_homework=base_homework).exists():
            sample_homework = SampleHomeWork.objects.filter(student=request.user,
                                                            base_homework=base_homework).last()
        else:
            sample_homework = SampleHomeWork.objects.create(student=request.user, base_homework=base_homework)
            for base_question in base_homework.questions.all():
                sample_question = self.make_sample_question(base_question.id)
                SampleQuestion.objects.create(base_question=base_question,
                                            text=sample_question["text"],
                                            true_answer=sample_question["answer"],
                                            homework=sample_homework)
                
        sample_questions = SampleQuestion.objects.filter(homework=sample_homework)
        student_name = str(request.user.first_name) + " " + str(request.user.last_name)
        # serializer = SampleQuestionSerializer(sample_questions, many=True)
        # return Response(serializer.data, status.HTTP_201_CREATED)
        template = get_template("learning/questions_pdf.html")
        context = {"sample_questions": sample_questions,
                   "title": base_homework.title,
                   "student_name": student_name
                   }
        html = template.render(context)
        pdf = pdfkit.from_string(html, False, options={"enable-local-file-access": ""})
        response = HttpResponse(pdf, content_type='application/pdf')
        file_name = f"sample_homework_{sample_homework.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    

class GetTeacherKeyAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request: Request):
        if request.user.role == 'TEACHER':
            if request.user.key:
                key = request.user.key
            else:
                key = get_random_string(length=8)
                request.user.key = key
                request.user.save()
            return Response({"key": key}, status.HTTP_200_OK)
        return Response({"message": "You should be teacher to get key."}, status.HTTP_403_FORBIDDEN)
    

class AddTeacherAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request: Request):
        try:
            key = request.data["key"]
        except:
            return Response({"message": "'key' is required."})
        if request.user.role == "STUDENT":
            try:
                teacher = User.objects.get(key=key)
            except User.DoesNotExist:
                return Response({"message": "Key is invalid."}, status.HTTP_400_BAD_REQUEST)
            request.user.teachers.add(teacher)
            return Response({"message": "You added to class."}, status.HTTP_200_OK)
        return Response({"message": "Not Allowed!"}, status.HTTP_403_FORBIDDEN)


class HomeWorkAnswerEvaluationAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request: Request):
        serializer = HomeWorkAnswerSerializer(data=request.data)
        if serializer.is_valid():
            sample_homework_id = serializer.data.get("sample_homework_id")
            try:
                sample_homework = SampleHomeWork.objects.get(id=sample_homework_id)
            except SampleHomeWork.DoesNotExist:
                return Response({"message": "Sample HomeWork does not exist"}, status.HTTP_404_NOT_FOUND)
            if sample_homework.student != request.user:
                return Response({"message": "This sample homework is not yours."})
            sample_homework_questions = SampleQuestion.objects.filter(homework=sample_homework)
            student_answers = serializer.data.get("questions")
            homework_answer = HomeWorkAnswer.objects.create(sample_homework=sample_homework, percent=0)
            true_answers = 0
            all_questions_num = sample_homework_questions.count()
            checked_questions_numbers = []
            # need to check for n+1 queries
            for student_answer in student_answers:
                if int(student_answer["question_num"]) not in checked_questions_numbers:    # to avoid recheck duplicate answer
                    for sample_question in sample_homework_questions:
                        if int(student_answer["question_num"]) == sample_question.number:
                            if student_answer["answer"] == sample_question.true_answer:
                                evaluation = True
                                true_answers += 1
                            else:
                                evaluation = False
                            QuestionAnswer.objects.create(sample_question=sample_question,
                                                        answer=student_answer["answer"],
                                                        homework_answer=homework_answer,
                                                        evaluation=evaluation)
                            checked_questions_numbers.append(int(student_answer["question_num"]))
            if all_questions_num != 0:
                percent = (true_answers / all_questions_num) * 100
                homework_answer.percent = percent
                homework_answer.save()
            return Response({"message": f"Your answer saved. Your percent is {percent}"}, status.HTTP_201_CREATED)

        else:
            return Response({"Error(s)": serializer.errors}, status.HTTP_400_BAD_REQUEST)