from django.urls import path

from comment import consumers


websocket_urlpatterns = [
    path("ws/comments/", consumers.CommentConsumer.as_asgi()),
]
