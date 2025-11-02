from rest_framework import serializers

from chat_app.models import Room, User


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
        extra_kwargs = {
            "name": {"read_only": True},
        }


class RoomCreateUpdateSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )

    class Meta:
        model = Room
        fields = ['name', 'participants']

    def create(self, validated_data):
        participants = validated_data.pop("participants", [])
        room = Room.objects.create(**validated_data)
        if participants:
            room.participants.set(participants)
        return room

    def update(self, instance: Room, validated_data):
        name = validated_data.get("name", None)
        if name and name != instance.name:
            if Room.objects.filter(name=name).exclude(id=instance.id).exists():
                raise serializers.ValidationError({"name": "Комната с таким именем уже существует."})
            instance.name = name

        participants = validated_data.get('participants', None)
        if participants is not None:
            instance.participants.set(participants)

        instance.save()
        return instance

