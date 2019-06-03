from rest_framework import serializers
from django.contrib.auth.models import User
from emails.models import Email, Attachment, SecurityAnswer


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(required=True, allow_blank=False)

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data

        """
        return User.objects.get(username=validated_data['username'])


class EmailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    subject = serializers.CharField(required=True, allow_blank=False, max_length=100)
    message = serializers.CharField(required=True, allow_blank=False)
    attachment = serializers.BooleanField(allow_null=True)
    created_at = serializers.DateTimeField()
    sender = UserSerializer()
    receiver = UserSerializer()

    def create(self, validated_data):
        """
        Create and return a new `Email` instance, given the validated data

        """
        sender_data = validated_data.pop('sender')
        receiver_data = validated_data.pop('receiver')

        sender = User.objects.get(username=sender_data['username'])
        receiver = User.objects.get(username=receiver_data['username'])

        validated_data['sender'] = sender
        validated_data['receiver'] = receiver

        return Email.objects.create(**validated_data)