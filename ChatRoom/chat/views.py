from django.shortcuts import render
from django.http import JsonResponse
from .models import Profil, ChatRoom
from .serializers import ChatRoomSerializer, ProfilSerializer
from rest_framework.viewsets import ModelViewSet


def index(req):
    return render(req, 'index.html')


class ApiProfil(ModelViewSet):
    queryset = Profil.objects.all()
    serializer_class = ProfilSerializer


class ApiChatRoom(ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
