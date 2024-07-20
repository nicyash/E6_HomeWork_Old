import json
from django.contrib.auth.models import User
from .models import ChatRoom, Message, Profil
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


def messagelist(id):
    objects = Message.objects.filter(chat_room=id)
    name = ChatRoom.objects.get(id=id).name
    list = {'MessageList': name}
    for object in objects:
        message = {object.author.user.first_name: object.message_text}
        list[object.id] = message
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

        if 'replacement' in message:
            if message['replacement'] == 'changeFirstName':
                id = message['id']
                name = message['name']
                user = User.objects.get(id=id)
                user.first_name = name
                user.save()

        if 'delete_room' in message:
            id = message['delete_room']
            print('комната с ID', id, "удалена")
            room = ChatRoom.objects.get(id=id)
            room.delete()
            print('комната с ID', id, "удалена")
            # async_to_sync(self.channel_layer.group_send)("all_instructions",
            #                                              {"type": "all_user", "order": "send_list_rooms"})

        if 'create_room' in message:
            name = message['create_room']
            if not ChatRoom.objects.filter(name=name).exists():
                room = ChatRoom(name=name)
                room.save()
                # async_to_sync(self.channel_layer.group_send)("all_instructions",
                #                                              {"type": "all_user", "order": "send_list_rooms"})
            else:
                self.send(json.dumps({'message': 'Выбери другое имя'}))
                print('совпадение имени комнаты')

        if 'change_room' in message:
            id = message['change_room']
            name = message['name']
            if not ChatRoom.objects.filter(name=name).exists():
                room = ChatRoom.objects.get(id=id)
                room.name = name
                room.save()
                # async_to_sync(self.channel_layer.group_send)("all_instructions",
                #                                              {"type": "all_user", "order": "send_list_rooms"})
            else:
                self.send(json.dumps({'message': 'Выбери другое имя'}))
                print('совпадение имени комнаты')

        if 'load' in message:
            if message['load'] == 'messageList':
                self.send(json.dumps(messagelist(message['room_id'])))

        if 'usersendcommandroom' in message:
            if message['usersendcommandroom'] == 'message':
                room_id = str(message['room_id'])
                user_id = message['userid']
                message = message['message']
                print(room_id, user_id, message)
                message_save = Message(author=Profil.objects.get(user=user_id), chat_room=ChatRoom.objects.get(id=room_id), message_text=message)
                message_save.save()
                print('Сообщение', message, 'сохранено в базе')
                # async_to_sync(self.channel_layer.group_send)(room_id, {"type": "incoming_message", "order": "accept_message", "name": username, "message": message})
                print('Сообщение', message, 'отправлено в комнату', room_id)