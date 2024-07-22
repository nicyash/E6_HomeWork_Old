from rest_framework import serializers
from .models import Profil, ChatRoom
from django.contrib.auth.models import User


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ('id', 'name')


class ProfilSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')

    class Meta:
        model = Profil
        fields = ('user', 'first_name', 'avatar', 'room')
