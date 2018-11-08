from django.contrib import admin
from Module_CommunicationManagement import views
from django.urls import path

urlpatterns = [
    path('instructor/TelegramManagement/',views.faculty_telegram_Base,name='faculty_telegram_Base'),
    path('instructor/TelegramManagement/update/chat_members/',views.faculty_telegram_UpdateChatMembers,name='faculty_telegram_UpdateChatMembers'),
    path('instructor/TelegramManagement/create/group/',views.faculty_telegram_CreateGroup,name='faculty_telegram_CreateGroup'),
    path('instructor/TelegramManagement/create/channel/',views.faculty_telegram_CreateChannel,name='faculty_telegram_CreateChannel'),
    path('instructor/TelegramManagement/sendMessage/',views.faculty_telegram_SendMessage,name='faculty_telegram_SendMessage'),
]
