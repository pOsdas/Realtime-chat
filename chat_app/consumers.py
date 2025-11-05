import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, Room

logger = logging.getLogger(__name__)

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        user = self.scope["user"]
        username = user.username if user.is_authenticated else "Anonymous"
        # приветственное сообщение
        await self.send(text_data=json.dumps({
            "message": f"Подключено к комнате: {self.room_name} as {username}"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError as e:
            logger.warning(f"Ошибка JSON: {e} | text_data: {repr(text_data)} — игнорируем")
            return

        message = data.get("message")

        if not message:
            return

        user = self.scope.get("user")
        username = user.username if user and user.is_authenticated else "Anonymous"

        await self.save_message(username, self.room_name, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "username": username,
                "message": message,
            }
        )

    async def chat_message(self, event):
        """Получить сообщение redis и отправить всем участникам"""
        await self.send(text_data=json.dumps({
            "username": event["username"],
            "message": event["message"],
        }))

    @database_sync_to_async
    def save_message(self, username, room_name, message):
        user = User.objects.filter(username=username).first()
        room = Room.objects.filter(name=room_name).first()
        if room and user:
            Message.objects.create(user=user, room=room, content=message)
