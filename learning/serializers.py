from rest_framework import serializers

from .models import Question, HomeWork

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['text', 'variable', 'variable_min', 'variable_max', 'true_answer']


class HomeWorkSerializer(serializers.ModelSerializer):
    questions = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='text'
    )
    
    class Meta:
        model = HomeWork
        fields = ['title', 'questions']
