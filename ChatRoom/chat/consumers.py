import json
from django.contrib.auth.models import User
from .models import ChatRoom, Message, Profil
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


def messagelist(id):
    messages = Message.objects.filter(chat_room=id)
    name = ChatRoom.objects.get(id=id).name
    list = {'MessageList': name}
    for message in messages:
        msg = {message.author.user.first_name: message.message_text}
        list[message.id] = msg
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
            async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_rooms"})

        if 'create_room' in message:
            name = message['create_room']
            if not ChatRoom.objects.filter(name=name).exists():
                room = ChatRoom(name=name)
                room.save()
                async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_rooms"})
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
                async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_rooms"})
            else:
                self.send(json.dumps({'message': 'Выбери другое имя'}))
                print('совпадение имени комнаты')

        if 'load' in message:
            if message['load'] == 'messageList':
                self.send(json.dumps(messagelist(message['room_id'])))


class WSChat(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(json.dumps({'message': 'подключились к комнате'}))
        async_to_sync(self.channel_layer.group_add)("all_chat", self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("all_chat", self.channel_name)

    def incoming_message(self, text_data=None):
        message = text_data
        print('входящее сообщение 1 из группы:', message)
        if message['order'] == "accept_message":
            name = message['name']
            message = message['message']
            self.send(json.dumps({'message': message, 'name': name}))
            print('сообщение принято клиентом')

    def all_chats(self, text_data=None):
        message = text_data
        print('входящее сообщение 2 из группы:', message)

    def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)
        print('incoming path:', self.scope["path"])
        print('входящее сообщение 3 из группы:', message)

        if 'usersendcommandroom' in message:
            if message['usersendcommandroom'] == 'roomselect':
                if message['oldroom_id'] != '':
                    oldroom_id = str(message['oldroom_id'])
                    async_to_sync(self.channel_layer.group_discard)(oldroom_id, self.channel_name)
                    print('Произошло отключение от комнаты', oldroom_id)
                newroom_id = str(message['newroom_id'])
                async_to_sync(self.channel_layer.group_add)(newroom_id, self.channel_name)
                print('Произошло подключение к комнате', newroom_id)


            if message['usersendcommandroom'] == 'message':
                room_id = str(message['room_id'])
                user_id = message['userid']
                message = message['message']
                user_first_name = User.objects.get(id=user_id).first_name
                print(user_first_name)
                print(room_id, user_id, message)
                message_save = Message(author=Profil.objects.get(user=user_id), chat_room=ChatRoom.objects.get(id=room_id), message_text=message)
                message_save.save()
                print('Сообщение', message, 'сохранено в базе')
                async_to_sync(self.channel_layer.group_send)(room_id, {"type": "incoming_message", "order": "accept_message", "name": user_first_name, "message": message})
                print('Сообщение', message, 'отправлено в комнату', room_id)
