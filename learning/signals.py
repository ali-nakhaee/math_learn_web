from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed

from .models import Question, SampleQuestion, QuestionAnswer, HomeWorkAnswer, HomeWork
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


@receiver(post_save, sender=SampleQuestion)
def reevaluate_answers(sender, instance, created, **kwargs):
    """ To deleting previous student answers to the sample question
    that changed and reevaluate homework_answers """
    if not created:
        question_answers = QuestionAnswer.objects.filter(sample_question=instance)
        question_answers.update(answer=None, evaluation=False)
        homework_answers = HomeWorkAnswer.objects.filter(questions__in=question_answers)
        for homework_answer in homework_answers:
            sample_homework = homework_answer.sample_homework
            all_questions_num = SampleQuestion.objects.filter(homework=sample_homework).count()
            true_answers_num = QuestionAnswer.objects.filter(homework_answer=homework_answer, evaluation=True).count()
            if all_questions_num != 0:
                percent = (true_answers_num / all_questions_num) * 100
            else:
                percent = 0
            homework_answer.percent = percent
            homework_answer.save()


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
