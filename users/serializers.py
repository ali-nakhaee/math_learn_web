from rest_framework import serializers

from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # need validators
        user = User(username=validated_data['username'], role=validated_data['role'])
        user.set_password(validated_data['password'])
        user.save()
        return user