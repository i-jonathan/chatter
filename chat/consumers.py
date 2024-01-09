import json
from datetime import datetime, timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import ChatRoom, ChatMessage, retrieveChatRoom
from asgiref.sync import sync_to_async


class ChatClient(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        current_user = self.scope["user"]
        self.room_name = f"rc_{self.room_id}"

        # handle the room permissions. Creating or fetching, managing who joins
        room = await retrieveChatRoom(self.room_id)
        if room is None:
            room = ChatRoom(room_id=self.room_id)
            await room.asave()

        # populate the user one and user two. Synchronous request would not work
        user_one = await sync_to_async(lambda: room.user_one)()
        user_two = await sync_to_async(lambda: room.user_two)()

        # multiple conditions to account for since it's 1 to 1 messaging
        # - Allow reconnectiong if user is already in the room
        # - if both users are already 'registered' in the room, don't allow new users
        # - if there is an open slot in the room, allow the user to 'register' to the room and connect
        if current_user in [user_one, user_two]:
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            return await self.accept()

        if user_one is not None and user_two is not None:
            return await self.close()

        if user_one is not None and user_two is None:
            room.user_two = self.scope["user"]

        if user_one is None:
            room.user_one = self.scope["user"]

        await room.asave()
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data, bytes_data=None):
        current_date = datetime.now(timezone.utc)
        # store message sent and offload updating other connections to chat_message
        message = ChatMessage(
            message=text_data,
            date_time=current_date,
            seen=False,
            sender=self.scope["user"],
            room=await retrieveChatRoom(self.room_id),
        )
        await message.asave()
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "date": current_date.strftime("%Y-%m-%d"),
                "time": current_date.strftime("%H:%M:%SZ%z"),
                "message": text_data,
                "read_status": message.seen,
                "sender_channel": self.channel_name,
            },
        )

    async def chat_message(self, event):
        if self.channel_name != event["sender_channel"]:
            message = event["message"]
            await self.send(
                text_data=json.dumps(
                    {
                        "message": message,
                        "date": event["date"],
                        "time": event["time"],
                        "read_status": event["read_status"],
                    }
                )
            )
