import os
import logging
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comments_app.settings")
django.setup()

import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.db import close_old_connections

ALGORITHM = "HS256"


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


@database_sync_to_async
def get_user(token: str | None) -> AnonymousUser | get_user_model():
    """Get user from db by access token"""
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

    except jwt.ExpiredSignatureError:
        logging.info("Signature expired")
        return AnonymousUser()

    except jwt.InvalidTokenError:
        logging.info("Token is invalid")
        return AnonymousUser()

    try:
        user = get_user_model().objects.get(id=decoded.get("user_id"))
        logging.info(f"user from db {user}")

    except get_user_model().DoesNotExist:
        return AnonymousUser()

    return user


class TokenAuthMiddleware(BaseMiddleware):
    """Token middleware"""
    async def __call__(self, scope, receive, send):
        close_old_connections()
        try:
            token_key = (dict((x.split("=") for x in scope["query_string"].decode().split("&")))).get("token", None)
        except ValueError:
            token_key = None

        scope["user"] = await get_user(token_key)
        logging.info(f"User authorized: {scope['user']}")
        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    """JWT AuthMiddleware"""
    return TokenAuthMiddleware(inner)
