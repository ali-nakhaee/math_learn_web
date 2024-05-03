import random
from sympy import sympify, symbols
from .models import Question


def make_sample_question(base_question_id):
    """ Function to make sample question from base question """
    
    base_question = Question.objects.get(id=base_question_id)
    sample_variable = random.randint(base_question.variable_min, base_question.variable_max)
    sample_question_text = base_question.text.replace(base_question.variable, str(sample_variable))
    expression = base_question.true_answer
    x = symbols(base_question.variable)
    answer_function = sympify(expression)
    sample_question_answer = float(answer_function.subs(x, sample_variable))
    return {"text": sample_question_text, "answer": sample_question_answer}
