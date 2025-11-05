import logging
import urllib.parse
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.backends import TokenBackend
from channels.db import database_sync_to_async

from chat_app.config import pydantic_settings

logger = logging.getLogger(__name__)

User = get_user_model()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app
        algorithm = settings.SIMPLE_JWT.get("ALGORITHM", "HS256")
        self.token_backend = TokenBackend(
            algorithm=algorithm,
            signing_key=pydantic_settings.secret_key
        )

    async def __call__(self, scope, receive, send):
        scope = dict(scope)

        instance = JWTAuthMiddlewareInstance(scope, self.app, self.token_backend)
        return await instance(receive, send)


class JWTAuthMiddlewareInstance:
    def __init__(self, scope, app, token_backend):
        self.scope = scope
        self.app = app
        self.token_backend = token_backend

    async def __call__(self, receive, send):
        self.scope["user"] = AnonymousUser()

        try:
            # Извлекаем токен из query string
            query_string = self.scope.get("query_string", b"").decode()
            token = None

            if query_string:
                qs = urllib.parse.parse_qs(query_string)
                token_list = qs.get("token") or qs.get("access_token") or qs.get("jwt")
                if token_list:
                    token = token_list[0]

            # Пытаемся аутентифицировать пользователя
            if token:
                await self._authenticate_token(token)

        except Exception as e:
            logger.error(f"Ошибка авторизации: {str(e)}")

        # Передаем управление следующему middleware/route
        return await self.app(self.scope, receive, send)

    async def _authenticate_token(self, token: str):
        try:
            payload = self.token_backend.decode(token, verify=False)
            user_id_claim = getattr(settings, "SIMPLE_JWT", {}).get("USER_ID_CLAIM", "user_id")
            user_id = payload.get(user_id_claim)

            if user_id:
                user = await database_sync_to_async(self._get_user)(user_id)
                if user:
                    self.scope["user"] = user
        except Exception as e:
            logger.error(f"Ошибка декодирования токена: {str(e)}")

    def _get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
