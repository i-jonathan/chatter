from django.db import models
from account.models import User


class ChatRoom(models.Model):
    room_id = models.CharField(max_length=10)
    user_one = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="user_one", null=True
    )
    user_two = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="user_two", null=True
    )


class ChatMessage(models.Model):
    message = models.TextField()
    date_time = models.DateTimeField()
    seen = models.BooleanField(default=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="chat_room"
    )

    class Meta:
        ordering = ("date_time",)


async def retrieveChatRoom(room_id: str) -> ChatRoom | None:
    try:
        room = await ChatRoom.objects.aget(room_id=room_id)
        return room
    except ChatRoom.DoesNotExist:
        return None
