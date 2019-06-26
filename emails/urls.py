from django.urls import path, re_path
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from emails.views import current_user, UserRegistration, UserInbox, UserSent, EmailAttachment, UserStarred, UserTrash

urlpatterns = [
    # Authentication related paths
    path('registration/', UserRegistration.as_view()),
    path('token-auth/', obtain_jwt_token),
    path('api-token-verify/', verify_jwt_token),
    path('admin/', admin.site.urls),

    # User related paths
    path('current-user/', current_user),
    path('inbox/', UserInbox.as_view()),
    path('sent/', UserSent.as_view()),
    path('attachments/', EmailAttachment.as_view()),
    path('starred/', UserStarred.as_view()),
    path('trash/', UserTrash.as_view()),
]