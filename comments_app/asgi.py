import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comments_app.settings")
django_asgi_app = get_asgi_application()

from comment.routing import websocket_urlpatterns
from comment.middleware import JwtAuthMiddlewareStack


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket":
            SessionMiddlewareStack(
                JwtAuthMiddlewareStack(URLRouter(websocket_urlpatterns))
            )
    }
)
