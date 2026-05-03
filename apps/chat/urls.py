from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path("mon-chat/", views.my_chat, name="my_chat"),
    path("<str:room_name>/", views.chat_room, name="room"),
    path("<str:room_name>/historique/", views.chat_history, name="history"),
]
