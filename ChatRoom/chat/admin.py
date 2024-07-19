from django.contrib import admin
from .models import Profil, ChatRoom, Message


admin.site.register(ChatRoom)
admin.site.register(Profil)
admin.site.register(Message)
