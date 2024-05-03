from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Question, SampleQuestion, QuestionAnswer
from .math_functions import make_sample_question


@receiver(post_save, sender=Question)
def change_sample_questions(sender, instance, created, **kwargs):
    """ Function for changing sample questions that are based on changed base question """
    if not created:
        sample_questions = SampleQuestion.objects.filter(base_question=instance)
        for sample_question in sample_questions:
            new_sample_question = make_sample_question(instance.id)
            sample_question.text = new_sample_question["text"]
            sample_question.true_answer = new_sample_question["answer"]
            print("change sample question signal ")
            sample_question.save()



@receiver(post_save, sender=SampleQuestion)
def reevaluate_answers(sender, instance, created, **kwargs):
    """ Function for deleting previous student answers to the sample question that changed """
    if not created:
        question_answers = QuestionAnswer.objects.filter(sample_question=instance)
        question_answers.update(answer=None, evaluation=False)
        print("reevaluate signal")
            