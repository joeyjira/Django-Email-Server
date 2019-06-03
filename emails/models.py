from django.db import models
from django.contrib.auth.models import User


class Email(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField(max_length=4000)
    attachment = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, related_name='sent', on_delete=models.DO_NOTHING, null=True)
    receiver = models.ForeignKey(User, related_name='inbox', on_delete=models.DO_NOTHING, null=True)


class Attachment(models.Model):
    name = models.CharField(max_length=100)
    URI = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=100)
    attached_to = models.ForeignKey(Email, related_name='attachments', on_delete=models.CASCADE)


class SecurityAnswer(models.Model):
    question_id = models.IntegerField()
    answer = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_by = models.ForeignKey(User, related_name="answers", on_delete=models.CASCADE)
