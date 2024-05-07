from rest_framework import serializers

from .models import Question, HomeWork, SampleQuestion, HomeWorkAnswer, Containing


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
        fields = ['title', 'questions', 'id', 'is_published']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def validate(self, attrs):
        try:
            questions = self.initial_data["questions"]
        except:
            raise serializers.ValidationError("Required field: 'questions'")
        for question in questions:
            try:
                id = question["id"]
                score = question["score"]
            except:
                raise serializers.ValidationError("For each question 'id' and 'score' fields are required.")
        return attrs

    def create(self, validated_data):
        """ Get questions id and score, check teacher of questions and add questions to homework"""
        user = self.context["request"].user
        questions = []
        for question_data in self.initial_data['questions']:
            question_id = question_data["id"]
            score = question_data["score"]
            try:
                question = Question.objects.get(id=question_id)
                if question.teacher == user:
                    questions.append((question_id, score))
            except:
                continue

        homework = HomeWork.objects.create(teacher=user, **validated_data)
        for idx, question in enumerate(questions, start=1):
            question_id = question[0]
            score = question[1]
            homework.questions.add(question_id, through_defaults={"number": idx, "score": score})
        return homework


class SampleQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleQuestion
        fields = ['text', 'true_answer']


class QuestionAnswerSerializer(serializers.Serializer):
    question_num = serializers.IntegerField()
    answer = serializers.FloatField()


class HomeWorkAnswerSerializer(serializers.Serializer):
    questions = QuestionAnswerSerializer(many=True)
    sample_homework_id = serializers.IntegerField()
