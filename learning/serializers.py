from rest_framework import serializers

from .models import Question, HomeWork


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
        fields = ['title', 'questions']

    def create(self, validated_data):
        """ Get question_ids, check teacher of questions and add questions to homework"""
        user = self.context["request"].user
        question_ids = []
        for question_id in self.initial_data['questions']:
            try:
                question = Question.objects.get(id=question_id)
                if question.teacher == user:
                    question_ids.append(question_id)
            except:
                continue

        homework = HomeWork.objects.create(**validated_data)
        for question_id in question_ids:
            homework.questions.add(question_id)
        return homework
