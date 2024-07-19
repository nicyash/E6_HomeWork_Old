import json
from django.contrib.auth.models import User
from .models import Profil, ChatRoom, Message
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


def userCard(user_id):
    objects = Profil.objects.filter(user_id=user_id)
    list = {'UserList': 'UserList'}
    for object in objects:
        list[object.id] = object.name
    return list


class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(json.dumps({'message': 'есть коннект!'}))
        async_to_sync(self.channel_layer.group_add)("all_instructions", self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("all_instructions", self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)

        if 'load' in message:
            user_id = message['load']
            self.send(json.dumps(userCard(user_id)))
            print('данные пользователя отправлены')

        if 'order' in message:
            if message['order'] == 'changeFirstName':
                id = message['id']
                name = message['name']
                user = User.objects.get(id=id)
                user.first_name = name
                user.save()

