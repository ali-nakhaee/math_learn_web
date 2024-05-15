""" learning.models file """
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Practice(models.Model):
    """ Base model for each learning course """
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)



class ConstantText(models.Model):
    """ Constant texts for each practice """
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    text = models.TextField()
    step = models.PositiveIntegerField()


class Answer(models.Model):
    """ Each blank field in one practice """
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    true_answer = models.CharField(max_length=50)
    step = models.PositiveIntegerField()


class Help(models.Model):
    """ Help texts for each practice """
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    step = models.PositiveIntegerField()


class Question(models.Model):
    """ Base question model """
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    variable = models.CharField(max_length=1)
    variable_min = models.IntegerField()
    variable_max = models.IntegerField()
    true_answer = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class HomeWork(models.Model):
    """ Base HomeWork model that contains some Questions """
    title = models.CharField(max_length=50)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question, through="Containing")
    date_created = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    total_score = models.FloatField()
    publish_date_start = models.DateTimeField(null=True)
    publish_date_end = models.DateTimeField(null=True)
    with_delay = models.BooleanField(default=True)
    delay_score = models.FloatField(default=0.8)

    def __str__(self):
        return self.title


class Containing(models.Model):
    """ Through table for M2M between homework and question """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    homework = models.ForeignKey(HomeWork, on_delete=models.CASCADE)
    number = models.IntegerField()
    score = models.FloatField(default=1)


class SampleHomeWork(models.Model):
    """ Sample homework for each student """
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    base_homework = models.ForeignKey(HomeWork, on_delete=models.PROTECT)
    date_created = models.DateTimeField(auto_now_add=True)


class SampleQuestion(models.Model):
    """ Sample question for each base question """
    base_question = models.ForeignKey(Question, on_delete=models.PROTECT)
    text = models.TextField()
    true_answer = models.FloatField()
    homework = models.ForeignKey(SampleHomeWork, on_delete=models.CASCADE, related_name="questions")


class HomeWorkAnswer(models.Model):
    sample_homework = models.ForeignKey(SampleHomeWork, on_delete=models.CASCADE)
    score = models.FloatField()
    date_created = models.DateTimeField(auto_now_add=True)
    with_delay = models.BooleanField(default=False)


class QuestionAnswer(models.Model):
    sample_question = models.ForeignKey(SampleQuestion, on_delete=models.CASCADE)
    answer = models.FloatField(null=True, blank=True)
    homework_answer = models.ForeignKey(HomeWorkAnswer, on_delete=models.CASCADE, related_name="questions")
    evaluation = models.BooleanField()
