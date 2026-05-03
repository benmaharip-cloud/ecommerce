import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")

# ⚠️ Django DOIT être initialisé avant tout import de modèles
django_asgi_app = get_asgi_application()
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path

# Import des consumers APRÈS django.setup()
from apps.chat.consumers import ChatConsumer

websocket_patterns = [
    re_path(r"ws/chat/(?P<room_name>[\w-]+)/$", ChatConsumer.as_asgi()),
]

try:
    from apps.notifications.consumers import NotificationConsumer
    websocket_patterns.append(
        re_path(r"ws/notifications/(?P<user_id>\d+)/$", NotificationConsumer.as_asgi())
    )
except Exception:
    pass

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_patterns)
    ),
})
