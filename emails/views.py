from django.db.models import QuerySet
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, permissions

from json import loads
import logging
import uuid

import boto3
from botocore.exceptions import ClientError

from emails.models import Attachment, Email, Starred, Inbox, Trash, Sent
from reply.secret import AWS_ACCESS, AWS_SECRET

from emails.serializers import UserSerializer, UserSerializerWithToken, EmailSerializer


@api_view(['GET'])
def current_user(request: Request):
    """
    Determine the current user by their token, and return their data
    """

    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserRegistration(APIView):
    """
    Create a new user
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request, format=None):
        serializer = UserSerializerWithToken(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInbox(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    """
    Receiver 'GET' request for user's inbox
    """
    def get(self, request: Request, format=None):
        emails = []

        # Get QuerySet for
        query = request.user.inbox

        for email_query in query.iterator():
            email = Email.objects.filter(id=email_query.email_id)

            if email.exists():
                serializer = EmailSerializer(email[0])
                emails.append(serializer.data)

        return Response({'inbox': emails}, status=status.HTTP_200_OK)

    """
    Receive 'POST' request to send message to another user's inbox
    """
    def post(self, request: Request, format=None):
        user: User = request.user
        files = request.FILES.getlist('attachments')
        email_data = loads(request.data['email'])

        email_data['sender'] = {'username': user.username}

        serializer = EmailSerializer(data=email_data)

        if serializer.is_valid():
            email = serializer.save()

            for file in files:
                object_name = str(uuid.uuid4()) + '_' + file.name

                attachment_data = {
                    'name': file.name,
                    'object_name': object_name,
                    'email': email,
                }

                Attachment.objects.create(**attachment_data)
                self.upload_file(file, "reply-django-server", object_name)

            receiver = User.objects.get(username=email_data['receiver']['username'])
            Inbox.objects.create(user=receiver, email=email)
            Sent.objects.create(user=user, email=email)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    """
    Receive 'PUT' request to update email status
    """
    def put(self, request: Request):
        email = Email.objects.get(id=request.query_params.get('email_id'))
        serializer = EmailSerializer(email, data=request.data)

        if serializer.is_valid():
            serializer.save()

        return Response({'email': 'read'}, status=status.HTTP_200_OK)

    """
    Receive 'DELETE' request to remove email from user's inbox and move to trash
    """
    def delete(self, request, format=None):
        user = request.user
        email_ids = request.query_params.get('email_id').split(',')

        for email_id in email_ids:
            email = Email.objects.get(id=email_id)
            Inbox.objects.get(user=user, email=email).delete()
            Trash.objects.create(**{'user': user, 'email': email})

        return Response(status=status.HTTP_200_OK)

    """
    Method to upload file to AWS S3 
    """
    def upload_file(self, file, bucket, object_name=None):
        if object_name is None:
            object_name = file.name

        # Upload the file
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS,
            aws_secret_access_key=AWS_SECRET
        )

        try:
            s3_client.upload_fileobj(file, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False

        return True


class UserSent(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    """
    Receiver 'GET' request for user's sent emails
    """
    def get(self, request: Request, format=None):
        emails = []

        # Get QuerySet for all emails user sent
        query = request.user.sent_email

        for email_query in query.iterator():
            email = Email.objects.filter(id=email_query.email_id)

            if email.exists():
                serializer = EmailSerializer(email[0])
                emails.append(serializer.data)

        return Response({'inbox': emails}, status=status.HTTP_200_OK)

    def delete(self, request: Request):
        """
        Delete email from user sent forever
        """
        user = request.user
        email_ids = request.query_params.get('email_id').split(',')

        for email_id in email_ids:
            email = Email.objects.get(id=email_id)
            Sent.objects.get(user=user, email=email).delete()

        return Response(status=status.HTTP_200_OK)


class UserStarred(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    """
    Receiver of requests for user's starred emails
    """

    def get(self, request: Request, format=None):
        emails = []

        starred_query: QuerySet = request.user.starred.all()

        for user_starred in starred_query.iterator():
            email = user_starred.email
            serializer = EmailSerializer(email)
            emails.append(serializer.data)

        return Response({'inbox': emails}, status=status.HTTP_200_OK)

    def post(self, request: Request, format=None):
        user = request.user
        email_ids = request.query_params.get('email_id').split(',')

        for email_id in email_ids:
            email = Email.objects.get(id=email_id)

            if Starred.objects.filter(user=user, email=email).exists():
                Starred.objects.filter(user=user, email=email).delete()
            else:
                Starred.objects.create(**{'user': user, 'email': email})

        return Response(status=status.HTTP_201_CREATED)


class UserTrash(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    """
    Receiver of requests for user's trash emails
    """

    def get(self, request: Request, format=None):
        emails = []

        trash_query: QuerySet = request.user.trash.all()

        for user_trash in trash_query.iterator():
            email = user_trash.email
            serializer = EmailSerializer(email)
            emails.append(serializer.data)

        return Response({'inbox': emails}, status=status.HTTP_200_OK)

    def patch(self, request: Request):
        user = request.user
        email_ids = request.query_params.get('email_id').split(',')

        for email_id in email_ids:
            email = Email.objects.get(id=email_id)

            if Trash.objects.filter(user=user, email=email).exists():
                Trash.objects.filter(user=user, email=email).delete()
                Inbox.objects.create(**{'user': user, 'email': email})

        return Response(status=status.HTTP_200_OK)

    def delete(self, request: Request):
        """
        Delete email from user Trash forever
        """
        user = request.user
        email_ids = request.query_params.get('email_id').split(',')

        for email_id in email_ids:
            email = Email.objects.get(id=email_id)
            Trash.objects.get(user=user, email=email).delete()

        return Response(status=status.HTTP_200_OK)


class EmailAttachment(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request):
        expiration = 300
        attachments = []
        email_id = request.query_params.get('email_id')
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS,
            aws_secret_access_key=AWS_SECRET
        )

        email: Email = Email.objects.get(id=email_id)

        attachment_query: QuerySet = email.attachments.all()

        for attachment in attachment_query.iterator():
            file_name = attachment.name
            object_name = attachment.object_name

            # Generate presigned url for client side to download resource
            presigned_url = s3_client\
                .generate_presigned_url('get_object',
                                        Params={'Bucket': 'reply-django-server',
                                                'Key': object_name},
                                        ExpiresIn=expiration)
            attachments.append({file_name: presigned_url})

        return Response({'attachments': attachments}, status=status.HTTP_200_OK)








