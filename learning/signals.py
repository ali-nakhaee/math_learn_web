from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Question, SampleQuestion
from .math_functions import make_sample_question


@receiver(post_save, sender=Question)
def change_sample_questions(sender, instance, created, **kwargs):
    if not created:
        sample_questions = SampleQuestion.objects.filter(base_question=instance)
        for sample_question in sample_questions:
            new_sample_question = make_sample_question(instance.id)
            sample_question.text = new_sample_question["text"]
            sample_question.true_answer = new_sample_question["answer"]
            sample_question.save()
            