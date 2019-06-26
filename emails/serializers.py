from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from emails.models import Email, Attachment, SecurityAnswer


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False)

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data

        """
        return User.objects.get(username=validated_data['username'])

    def validate_username(self, value):
            user_query = User.objects.filter(username=value)
            if len(user_query) == 0:
                raise serializers.ValidationError("User does not exist. Try another.")

            return value


class UserSerializerWithToken(serializers.Serializer):
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)
    username = serializers.CharField(required=True, allow_blank=False, min_length=3)
    password = serializers.CharField(required=True, write_only=True, min_length=8)
    confirm = serializers.CharField(required=True, write_only=True, min_length=8)
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)

        return token

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('confirm')
        instance = User(**validated_data)

        if password is not None:
            instance.set_password(password)
            instance.save()
            return instance

    def validate(self, data: dict):
        errors = {}

        if User.objects.filter(username=data.get('username')).exists():
            errors['usernameError'] = "That username is taken. Try another."

        if data.get('password') != data.get('confirm'):
            errors['confirmError'] = "Password does not match. Try again."

        if errors:
            raise serializers.ValidationError(errors)

        return data


class AttachmentSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, allow_blank=False)
    object_name = serializers.CharField(required=True, allow_blank=False)
    created_at = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        """

        :param validated_data:
        :return: Instance of Attachment model
        """

        return Attachment.objects.create(**validated_data)


class EmailSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    subject = serializers.CharField(required=True, allow_blank=False, max_length=100)
    message = serializers.CharField(required=True, allow_blank=False)
    read = serializers.BooleanField(required=False)
    created_at = serializers.DateTimeField(required=False)
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

    def update(self, instance, validated_data):
        instance.read = validated_data.get('read', instance.read)
        instance.save()

        return instance
