from django.db import transaction
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from chat_app.models import User
from chat_app.api.v1.tokens import TokensSerializer, TokensRefreshParamsSerializer, TokenObtainPairParamsSerializer

logger = logging.getLogger(__name__)


class TokenObtainPairView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["JWT"],
        request=TokenObtainPairParamsSerializer,
        responses=TokensSerializer,
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ValidationError("username и password обязательны")

        from django.contrib.auth import authenticate
        user = authenticate(request=request, username=username, password=password)
        if not user:
            raise AuthenticationFailed("Не правильные credentials")

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh_str = str(refresh)

        user.refresh_token = refresh_str
        user.save(update_fields=["refresh_token"])

        data = {"access_token": access, "refresh_token": refresh_str, "token_type": "Bearer"}
        serializer = TokensSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokensRefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["JWT"],
        request=TokensRefreshParamsSerializer,
        responses=TokensSerializer,
    )
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            raise AuthenticationFailed("Не правильный refresh token")

        try:
            incoming = RefreshToken(refresh_token)
        except Exception as e:
            raise AuthenticationFailed(str(e))

        user_id = incoming.get("user_id")
        if not user_id:
            raise AuthenticationFailed("Не правильный token payload")

        with transaction.atomic():
            user = User.objects.select_for_update().filter(pk=user_id).first()
            if not user:
                raise AuthenticationFailed("Пользователь не найден")

            # Старый refresh в чс
            stored = user.refresh_token
            if not stored or stored != refresh_token:
                raise AuthenticationFailed("Refresh token устарел или не правильный")

            try:
                incoming.blacklist()
            except AttributeError as e:
                logger.warning("Ошибка при добавлении старого refresh в чс: %s", e)
            except TokenError as e:
                logger.warning("Ошибка при добавлении старого refresh в чс: %s", e)

            new_refresh = RefreshToken.for_user(user)
            new_access = str(new_refresh.access_token)
            new_refresh_str = str(new_refresh)

            # Сохраняем новый refresh
            user.refresh_token = new_refresh_str
            user.save(update_fields=["refresh_token"])

        data = {"access_token": new_access, "refresh_token": new_refresh_str, "token_type": "Bearer"}
        serializer = TokensSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

