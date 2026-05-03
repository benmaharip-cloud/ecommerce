import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage

User = get_user_model()

CHATBOT_RESPONSES = {
    "livraison": "La livraison prend 2-5 jours ouvrables. Vous pouvez suivre votre commande dans votre profil.",
    "retour": "Vous avez 30 jours pour retourner un article. Contactez notre SAV depuis votre espace client.",
    "paiement": "Nous acceptons CB, PayPal et virement bancaire. Toutes les transactions sont sécurisées.",
    "commande": "Pour suivre votre commande, rendez-vous dans Mes Commandes dans votre profil.",
    "stock": "Consultez la fiche produit pour voir la disponibilité en temps réel.",
}

def chatbot_reply(message: str) -> str | None:
    msg = message.lower()
    for kw, rep in CHATBOT_RESPONSES.items():
        if kw in msg:
            return rep
    return None


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        sender = self.scope["user"]
        if not message:
            return

        await self.save_message(self.room_name, sender, message, is_bot=False)

        await self.channel_layer.group_send(self.room_group, {
            "type": "chat_message",
            "message": message,
            "sender": sender.get_full_name() or sender.email,
            "is_bot": False,
        })

        # Chatbot response
        bot_reply = chatbot_reply(message)
        if bot_reply:
            await self.save_message(self.room_name, None, bot_reply, is_bot=True)
            await self.channel_layer.group_send(self.room_group, {
                "type": "chat_message",
                "message": bot_reply,
                "sender": "Assistant ShopDjango",
                "is_bot": True,
            })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, room_name, sender, content, is_bot):
        room, _ = ChatRoom.objects.get_or_create(name=room_name)
        ChatMessage.objects.create(room=room, sender=sender, content=content, is_bot=is_bot)
