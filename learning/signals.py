from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed

from .models import Question, SampleQuestion, QuestionAnswer, HomeWorkAnswer, HomeWork, Containing
from .math_functions import make_sample_question


@receiver(post_save, sender=Question)
def change_sample_questions(sender, instance, created, **kwargs):
    """ Function for changing publishing sample questions that are based on changed base question """
    if not created:
        sample_questions = SampleQuestion.objects.filter(base_question=instance,
                                                         homework__base_homework__is_published=True)
        for sample_question in sample_questions:
            new_sample_question = make_sample_question(instance.id)
            sample_question.text = new_sample_question["text"]
            sample_question.true_answer = new_sample_question["answer"]
            sample_question.save()
            # need to send email to student for this change
        print('change_sample_questions signal run.')


@receiver(post_save, sender=SampleQuestion)
def reevaluate_answers(sender, instance, created, **kwargs):
    """ To deleting previous student answers to the sample question
    that changed and reevaluate homework_answers """
    if not created:
        question_answers = QuestionAnswer.objects.filter(sample_question=instance)
        question_answers.update(answer=None, evaluation=False)
        homework_answers = HomeWorkAnswer.objects.filter(questions__in=question_answers)
        for homework_answer in homework_answers:
            new_score = 0
            # need better method with less queries
            for question_answer in homework_answer.questions.all():
                if question_answer.evaluation == True:
                    base_homework = homework_answer.sample_homework.base_homework
                    base_question = question_answer.sample_question.base_question
                    question_score = Containing.objects.get(question=base_question,
                                                            homework=base_homework).score
                    new_score += question_score
            homework_answer.score = new_score
            homework_answer.save()
        print('reevaluate_answers signal run.')


@receiver(m2m_changed, sender=HomeWork.questions.through)
def update_homework_total_score(sender, instance, action, **kwargs):
    if action == 'post_add' or action == 'post_remove':
        print("update_homework_total_score signal run.")
        total_score = 0
        for question in sender.objects.filter(homework=instance):
            total_score += question.score
        instance.total_score = total_score
        print(f"totla_score = {total_score}")
        instance.save()
