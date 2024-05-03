import json

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from learning.models import Question, HomeWork, SampleQuestion, SampleHomeWork, QuestionAnswer, HomeWorkAnswer
from users.models import User


class HomeWorkAnswerEvaluationViewTest(TestCase):
    def setUp(self):
        teacher = User.objects.create(username='teacher', password='123')
        base_question = Question.objects.create(teacher=teacher,
                                                text=' ',
                                                variable=' ',
                                                variable_min=0,
                                                variable_max=10,
                                                true_answer=' ')
        base_homework = HomeWork.objects.create(teacher=teacher,
                                                title=' ')
        base_homework.questions.add(base_question)
        sample_homework = SampleHomeWork.objects.create(student=teacher,
                                                        base_homework=base_homework)
        sample_question_1 = SampleQuestion.objects.create(base_question=base_question,
                                                          text="2+2=",
                                                          true_answer=4,
                                                          homework=sample_homework,
                                                          number=1)
        sample_question_2 = SampleQuestion.objects.create(base_question=base_question,
                                                          text="3+3=",
                                                          true_answer=6,
                                                          homework=sample_homework,
                                                          number=2)
        token = Token.objects.create(user=teacher)
        token.save()
        
    def test_does_not_exist_homework(self):
        """ Post data with 'sample_homework_id=2' that does not exist. """
        user_id = User.objects.get(username='teacher').id
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
        
