from django.db import models
from django.contrib.auth.models import User

class Email(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField(max_length=4000)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, related_name="sent", on_delete=models.DO_NOTHING, null=True)
    receiver = models.ForeignKey(User, related_name='emails', on_delete=models.DO_NOTHING, null=True)

    class Meta:
        ordering = ['-created_at']


class Attachment(models.Model):
    name = models.CharField(max_length=100)
    object_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.ForeignKey(Email, related_name='attachments', on_delete=models.DO_NOTHING, null=True)


class Inbox(models.Model):
    user = models.ForeignKey(User, related_name='inbox', on_delete=models.CASCADE, null=True)
    email = models.ForeignKey(Email, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Starred(models.Model):
    user = models.ForeignKey(User, related_name='starred', on_delete=models.CASCADE, null=True)
    email = models.ForeignKey(Email, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Sent(models.Model):
    user = models.ForeignKey(User, related_name='sent_email', on_delete=models.CASCADE, null=True)
    email = models.ForeignKey(Email, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Trash(models.Model):
    user = models.ForeignKey(User, related_name='trash', on_delete=models.CASCADE, null=True)
    email = models.ForeignKey(Email, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class SecurityAnswer(models.Model):
    question_id = models.IntegerField()
    answer = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_by = models.ForeignKey(User, related_name="answers", on_delete=models.CASCADE)
