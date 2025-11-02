from django.urls import path
from .room import CreateRoomView, DeleteRoomView, UpdateRoomView, GetRoomView, GetRoomsView

urlpatterns = [
    # Комнаты
    path('room/get/<int:room_id>/', GetRoomView.as_view(), name='get-room'),
    path('room/get-all/', GetRoomsView.as_view(), name='get-rooms'),
    path('room/create/', CreateRoomView.as_view(), name='create-room'),
    path('room/update/<int:room_id>/', UpdateRoomView.as_view(), name='update-room'),
    path('room/delete/<int:room_id>/', DeleteRoomView.as_view(), name='delete-room'),
]