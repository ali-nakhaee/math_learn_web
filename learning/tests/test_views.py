import json
from datetime import datetime, timezone, timedelta

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from learning.models import Question, HomeWork, SampleQuestion, SampleHomeWork, QuestionAnswer, HomeWorkAnswer
from users.models import User


class HomeWorkAnswerEvaluationViewTest(TestCase):
    def setUp(self):
        teacher = User.objects.create(username='teacher', password='123')
        student = User.objects.create(username='student', password='123')
        base_question_1 = Question.objects.create(teacher=teacher,
                                                text='2+x=',
                                                variable='x',
                                                variable_min=0,
                                                variable_max=10,
                                                true_answer='2 + x')
        base_question_2 = Question.objects.create(teacher=teacher,
                                                text='3+y=',
                                                variable='y',
                                                variable_min=0,
                                                variable_max=10,
                                                true_answer='3 + y')
        base_homework = HomeWork.objects.create(teacher=teacher,
                                                title='Base HomeWork',
                                                total_score=3,
                                                publish_date_start=datetime.now(timezone.utc) - timedelta(days=5),
                                                publish_date_end=datetime.now(timezone.utc) - timedelta(days=2))
        base_homework.questions.add(base_question_1, through_defaults={"number": 1, "score": 1})
        base_homework.questions.add(base_question_2, through_defaults={"number": 2, "score": 2})
        sample_homework = SampleHomeWork.objects.create(student=student,
                                                        base_homework=base_homework)
        sample_question_1 = SampleQuestion.objects.create(base_question=base_question_1,
                                                          text="2+2=",
                                                          true_answer=4,
                                                          homework=sample_homework)
        sample_question_2 = SampleQuestion.objects.create(base_question=base_question_2,
                                                          text="3+3=",
                                                          true_answer=6,
                                                          homework=sample_homework)
        teacher_token = Token.objects.create(user=teacher)
        teacher_token.save()
        student_token = Token.objects.create(user=student)
        student_token.save()
        
    def test_does_not_exist_homework(self):
        """ Post data with 'sample_homework_id=2' that does not exist. """
        user_id = User.objects.get(username='student').id
        token = Token.objects.get(user_id=user_id)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post("/homework_evaluation/", json.dumps({"questions": [
                                                                {"question_num": 1,
                                                                    "answer": 9},
                                                                {"question_num": 2,
                                                                    "answer": 18}],
                                                        "sample_homework_id": 2}),
                                                        content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_invalid_data(self):
        """ Post invalid data with key 'sample_homework_ids' """
        user_id = User.objects.get(username='student').id
        token = Token.objects.get(user_id=user_id)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post("/homework_evaluation/", json.dumps({"questions": [
                                                                {"question_num": 1,
                                                                    "answer": 9},
                                                                {"question_num": 2,
                                                                    "answer": 18}],
                                                        "sample_homework_ids": 1}),
                                                        content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["Error(s)"], {"sample_homework_id": ["This field is required."]})

    def test_student_owning_homework(self):
        """ Post data for not owning sample_homework """
        user_id = User.objects.get(username='teacher').id
        token = Token.objects.get(user_id=user_id)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post("/homework_evaluation/", json.dumps({"questions": [
                                                                {"question_num": 1,
                                                                    "answer": 9},
                                                                {"question_num": 2,
                                                                    "answer": 18}],
                                                        "sample_homework_id": 1}),
                                                        content_type="application/json")
        self.assertEqual(response.status_code, 403)

    def test_evaluation_process(self):
        """ Post correct data and check evaluation process """
        user_id = User.objects.get(username='student').id
        token = Token.objects.get(user_id=user_id)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post("/homework_evaluation/", json.dumps({"questions": [
                                                                {"question_num": 1,
                                                                    "answer": 4},
                                                                {"question_num": 2,
                                                                    "answer": 6}],
                                                        "sample_homework_id": 1}),
                                                        content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(QuestionAnswer.objects.all().count(), 2)
        self.assertEqual(HomeWorkAnswer.objects.get(id=1).raw_score, 3)
        self.assertEqual(HomeWorkAnswer.objects.get(id=1).with_delay, True)
        self.assertEqual(HomeWorkAnswer.objects.get(id=1).score, 2.4)

    def test_creating_blank_answers(self):
        """ Check creating blank answers """
        user_id = User.objects.get(username='student').id
        token = Token.objects.get(user_id=user_id)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post("/homework_evaluation/", json.dumps({"questions": [
                                                                {"question_num": 1,
                                                                    "answer": 4}],
                                                        "sample_homework_id": 1}),
                                                        content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(QuestionAnswer.objects.all().count(), 2)
        self.assertEqual(HomeWorkAnswer.objects.get(id=1).raw_score, 1)
        