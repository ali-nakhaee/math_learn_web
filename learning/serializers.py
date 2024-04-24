from rest_framework import serializers

from .models import Question, HomeWork, SampleQuestion


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'variable', 'variable_min', 'variable_max', 'true_answer']


class HomeWorkSerializer(serializers.ModelSerializer):
    questions = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='text'
    )
    # questions = QuestionSerializer(many=True, read_only=True)  # <--- another way to serialize questions
    
    class Meta:
        model = HomeWork
        fields = ['title', 'questions', 'id']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def create(self, validated_data):
        """ Get question_ids, check teacher of questions and add questions to homework"""
        user = self.context["request"].user
        question_ids = []
        for question_id in self.initial_data['questions']:
            try:
                question = Question.objects.get(id=question_id)
                if question.teacher == user:
                    if question_id not in question_ids:
                        question_ids.append(question_id)
            except:
                continue

        homework = HomeWork.objects.create(teacher=user, **validated_data)
        for question_id in question_ids:
            homework.questions.add(question_id)
        return homework


class SampleQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleQuestion
        fields = ['text', 'true_answer']