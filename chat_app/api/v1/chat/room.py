from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chat_app.api.v1.chat.serializers import RoomCreateUpdateSerializer, RoomSerializer
from chat_app.models import Room
from drf_spectacular.utils import extend_schema, OpenApiParameter
import logging

logger = logging.getLogger(__name__)


class GetRoomView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Room'],
        responses=RoomSerializer,
    )
    def get(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"detail": "Комната не найдена"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoomSerializer(room)
        logger.info("Запрошена информация о комнате '%s' пользователем %s", room.name, request.user.username)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetRoomsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Room'],
        responses=RoomSerializer(many=True),
    )
    def get(self, request):
        try:
            rooms = Room.objects.all()
        except Room.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)

        serializer = RoomSerializer(rooms, many=True)
        logger.info("Запрошена информация о комнатах пользователем %s", request.user.username)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateRoomView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Room'],
        request=RoomCreateUpdateSerializer,
        responses=RoomSerializer,
    )
    def post(self, request):
        serializer = RoomCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        out = RoomSerializer(room)
        logger.info("Создана комната '%s' пользователем %s", room.name, request.user.username)
        return Response(out.data, status=status.HTTP_201_CREATED)


class UpdateRoomView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Room'],
        request=RoomCreateUpdateSerializer,
        responses=RoomSerializer,
    )
    def patch(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"detail": "Комната не найдена"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoomCreateUpdateSerializer(instance=room, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        out = RoomSerializer(room)
        logger.info("Комната с id=%s обновлена пользователем %s", room.id, request.user.username)
        return Response(out.data, status=status.HTTP_200_OK)


class DeleteRoomView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Room'],
        request=RoomCreateUpdateSerializer,
        responses=RoomSerializer,
    )
    def delete(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"detail": f"Комната c id={room_id} не найдена"}, status=status.HTTP_404_NOT_FOUND)

        room.delete()
        logger.info("Комната с id=%s успешно удалена", room_id)
        return Response(
            {"message": f"Комната с id={room_id} успешно удалена"},
            status=status.HTTP_200_OK
        )




