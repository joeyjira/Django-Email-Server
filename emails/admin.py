from django.contrib import admin
from .models import Email, Attachment, SecurityAnswer

# Register your models here.
admin.site.register(Email)
admin.site.register(Attachment)
admin.site.register(SecurityAnswer)
