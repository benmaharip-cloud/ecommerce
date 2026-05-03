from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatRoom, ChatMessage

@login_required
def chat_room(request, room_name):
    room, _ = ChatRoom.objects.get_or_create(name=room_name)
    messages = room.messages.order_by("created_at")[:50]
    return render(request, "chat/room.html", {"room": room, "messages": messages})

@login_required
def my_chat(request):
    """Redirige le client vers sa salle personnelle."""
    room_name = f"client-{request.user.pk}"
    return chat_room(request, room_name)

@login_required
def chat_history(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)
    msgs = list(room.messages.order_by("created_at").values(
        "content", "is_bot", "created_at", "sender__email"
    ))
    return JsonResponse({"messages": msgs})
