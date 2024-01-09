import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import ChatRoom, ChatMessage
from account.models import User


@csrf_exempt
@require_http_methods(["PATCH"])
def update_read_status(requests, room_id):
    # set the status of all the latest unread messages to read
    # get all the messages where the sender is not the requesting user and the room
    # is the specified fetch_room_nessages
    # mark all as read and save
    headers = requests.headers
    if "Authorization" not in headers.keys():
        return JsonResponse({"message": "Unauthorized"}, status=401)

    try:
        user = User.objects.get(api_key=headers["Authorization"])
    except User.DoesNotExist:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    try:
        room = ChatRoom.objects.get(room_id=room_id)
    except ChatRoom.DoesNotExist:
        return JsonResponse({"message": "Requested room does not exist"}, status=404)

    if user not in [room.user_one, room.user_two]:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    _ = ChatMessage.objects.exclude(sender=user).filter(room=room).update(seen=True)
    return JsonResponse({"message": "Marked as Read"})


@require_http_methods(["GET"])
def fetch_room_messages(requests, room_id):
    # return the entire chat history of a particular chat room.
    # Get the room id from path parameters
    headers = requests.headers
    if "Authorization" not in headers.keys():
        return JsonResponse({"message": "Unauthorized"}, status=401)

    try:
        user = User.objects.get(api_key=headers["Authorization"])
    except User.DoesNotExist:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    try:
        room = ChatRoom.objects.get(room_id=room_id)
    except ChatRoom.DoesNotExist:
        return JsonResponse({"message": "Requested room does not exist"}, status=404)

    if user not in [room.user_one, room.user_two]:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    messages = ChatMessage.objects.filter(room=room).values(
        "message", "date_time", "seen", "sender", "room"
    )
    return JsonResponse({"result": list(messages)})
