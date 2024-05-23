from rest_framework import serializers

from .models import Question, HomeWork, SampleQuestion, HomeWorkAnswer, Containing


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'variable', 'variable_min', 'variable_max', 'true_answer']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ContainingSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(fields=('text', 'id'))
    class Meta:
        model = Containing
        fields = ['question', 'number', 'score']


class HomeWorkSerializer(serializers.ModelSerializer):
    # questions = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='text'
    # )
    # questions = QuestionSerializer(many=True, read_only=True)  # <--- another way to serialize questions
    questions = ContainingSerializer(source='containing_set', many=True, read_only=True)
    
    class Meta:
        model = HomeWork
        fields = ['title', 'questions', 'id', 'total_score', 'is_published', 'publish_date_start', 'publish_date_end']
        extra_kwargs = {"total_score": {"required": False}}

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
        """ Get questions id and score, check teacher of questions and add questions to homework based on received order."""
        user = self.context["request"].user
        homework = HomeWork.objects.create(teacher=user, total_score=0, **validated_data)
        containing_objects = []
        total_score = 0
        selected_questions = Question.objects.filter(
            id__in=(question["id"] for question in self.initial_data['questions']),
            teacher=user,
            )
        # to sort questions based on received order
        sorted_selected_questions = sorted(selected_questions,
                            key=lambda obj: list(question['id'] for question in self.initial_data['questions']).index(obj.id))
        
        for idx, selected_question in enumerate(sorted_selected_questions, start=1):
            for question in self.initial_data['questions']:
                if question['id'] == selected_question.id:
                    score = question['score']
                    break
            containing_objects.append(Containing(
                question=selected_question,
                homework=homework,
                number=idx,
                score=score
            ))
            total_score += score
        Containing.objects.bulk_create(containing_objects)
        homework.total_score = total_score
        homework.save()
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
