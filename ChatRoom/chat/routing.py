from django.urls import re_path
from .consumers import WSConsumer, WSChat


ws_urlpatterns = [
    re_path(r'ws/command/', WSConsumer.as_asgi()),
    re_path(r'ws/chat/', WSChat.as_asgi()),
]

channel_routing = {
    'websocket.connect': 'chat.consumers.WSConsumer.as_asgi()',
    'websocket.receive': 'chat.consumers.WSConsumer.as_asgi()',
    'websocket.disconnect': 'chat.consumers.WSConsumer.as_asgi()',
}
