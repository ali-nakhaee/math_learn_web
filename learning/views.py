""" learning.views file """

import pdfkit
from datetime import datetime, timezone

from django.utils.crypto import get_random_string
from django.template.loader import get_template
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.db.models import Prefetch

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated

from users.models import User
from .models import Practice, ConstantText, Answer, Help, Question, HomeWork, SampleHomeWork, SampleQuestion, HomeWorkAnswer, QuestionAnswer, Containing
from .serializers import QuestionSerializer, HomeWorkSerializer, SampleQuestionSerializer, HomeWorkAnswerSerializer
from .math_functions import make_sample_question


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
    """ Get homeworks list and Post to create a new homework for teacher"""
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        homeworks = HomeWork.objects.filter(teacher=request.user).order_by('-date_created').prefetch_related(
                            Prefetch('containing_set', queryset=Containing.objects.select_related('question')))
        serializer = HomeWorkSerializer(homeworks, many=True)
        data = serializer.data
        return Response(data, status.HTTP_200_OK)
    
    def post(self, request: Request):
        serializer = HomeWorkSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "HomeWork created."}, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class EditHomeWorkAPIView(APIView):
    # get, put, delete
    permission_classes = (IsAuthenticated,)
    
    def get(self, request: Request, base_homework_id):
        """ Return the base_homework detail and the list of answers to specific base_homework for teacher. """
        try:
            base_homework = HomeWork.objects.prefetch_related('containing_set__question').get(id=base_homework_id)
        except HomeWork.DoesNotExist:
            return Response({"message": "This homework does not exist."}, status.HTTP_404_NOT_FOUND)
        if base_homework.teacher != request.user:
            return Response({"message": "This homework is not yours."})
        sample_homeworks = SampleHomeWork.objects.filter(base_homework=base_homework)
        homework_answers = HomeWorkAnswer.objects.filter(sample_homework__in=sample_homeworks).select_related('sample_homework__student',
                                                                                                                'sample_homework__base_homework')
        student_list = []
        answers = []
        for homework_answer in homework_answers:
            student = homework_answer.sample_homework.student
            if student not in student_list:
                student_list.append(student)
                answers.append({"student_id": student.id,
                                "first_name": student.first_name,
                                "last_name": student.last_name,
                                "score": homework_answer.score,
                                "try_num": 1})
            else:
                for i in range(len(answers)):
                    if answers[i]["student_id"] == student.id:
                        if answers[i]["score"] < homework_answer.score:
                            answers[i]["score"] = homework_answer.score
                        answers[i]["try_num"] += 1
        data = [{"homework_details": HomeWorkSerializer(base_homework).data}, {"answers": answers}]
        return Response(data, status.HTTP_200_OK)


class HomeWorksListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        """ Return a list of published homeworks for the student. """
        homeworks = HomeWork.objects.filter(teacher__students=request.user,
                                            is_published=True,
                                            publish_date_start__lte=datetime.now(timezone.utc),
                                            publish_date_end__gte=datetime.now(timezone.utc))
        serializer = HomeWorkSerializer(homeworks, fields=('title', 'id'), many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class GetHomeWorkAPIView(APIView):
    """ To create a pdf file that contains sample questions for a specific homework for student. """
    permission_classes = (IsAuthenticated,)

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
                sample_question = make_sample_question(base_question.id)
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
                sample_homework = SampleHomeWork.objects.select_related(
                        'base_homework',
                        'student',
                    ).prefetch_related(
                        'questions',
                    ).get(id=sample_homework_id)
            except SampleHomeWork.DoesNotExist:
                return Response({"message": "Sample HomeWork does not exist"}, status.HTTP_404_NOT_FOUND)
            if sample_homework.student != request.user:
                return Response({"message": "This sample homework is not yours."}, status.HTTP_403_FORBIDDEN)
            if (datetime.now(timezone.utc) > sample_homework.base_homework.publish_date_end and
                sample_homework.base_homework.with_delay == False):
                return Response({"message": "Delay! The answer is not accepted."}, status.HTTP_403_FORBIDDEN)
            
            sample_homework_questions = sample_homework.questions.all()
            student_answers = serializer.data.get("questions")
            homework_answer = HomeWorkAnswer.objects.create(sample_homework=sample_homework, raw_score=0)
            score = 0
            message = {"message": "Your answer is saved."}
            # need to check for n+1 queries
            for sample_question in sample_homework_questions:
                for student_answer in student_answers:
                    if sample_question.number == student_answer["question_num"]:
                        if sample_question.true_answer == student_answer["answer"]:
                            evaluation = True
                        else:
                            evaluation = False
                        answer = student_answer["answer"]
                        break
                    else:
                        evaluation = False
                        answer = None
                QuestionAnswer.objects.create(sample_question=sample_question,
                                              answer=answer,
                                              homework_answer=homework_answer,
                                              evaluation=evaluation)
                if evaluation == True:
                    score += sample_question.score
                    message[f"question_num_{sample_question.number}"] = evaluation
                elif answer is not None:
                    message[f"question_num_{sample_question.number}"] = evaluation
                else:
                    message[f"question_num_{sample_question.number}"] = "Blank"
            

            if datetime.now(timezone.utc) > sample_homework.base_homework.publish_date_end:
                homework_answer.with_delay = True
            else:
                homework_answer.with_delay = False
            homework_answer.raw_score = score
            homework_answer.save()
            message["Final score"] = f"{round(homework_answer.score, 2)} / {sample_homework.base_homework.total_score}"
            return Response(message, status.HTTP_201_CREATED)

        else:
            return Response({"Error(s)": serializer.errors}, status.HTTP_400_BAD_REQUEST)
