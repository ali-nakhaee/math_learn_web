from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Question, SampleQuestion


@receiver(post_save, sender=Question)
def change_sample_questions(sender, instance, created, **kwargs):
    if not created:
        sample_questions = SampleQuestion.objects.filter(base_question=instance)
        
    