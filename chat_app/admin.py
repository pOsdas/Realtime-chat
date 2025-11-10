from django.contrib import admin
from .models import Room, Message, User
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'username', 'password', 'refresh_token', 'phone', 'email')}),
        ('Персональные данные', {
            'fields': ('first_name', 'last_name'),
            'classes': ('collapse',),
        })
    )

    add_fieldsets = (
        (None, {'fields': ('id', 'username', 'password1', 'password2', 'refresh_token', 'phone', 'email')}),
        ('Персональные данные', {
            'fields': ('first_name', 'last_name'),
            'classes': ('collapse',),
        }),
    )

    list_display = (
        'username', 'first_name', 'last_name', 'phone', 'email',
    )
    readonly_fields = ('id', 'refresh_token')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "get_participants_count")
    search_fields = ("id", "name")
    list_filter = ("name",)
    filter_horizontal = ("participants",)

    def get_participants_count(self, obj):
        return obj.participants.count()
    get_participants_count.short_description = "Кол-во участников"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "timestamp", "content", "user", "short_content")
    search_fields = ("id", "content", "user__username", "room__name")
    list_filter = ("timestamp", "room", "user")

    def short_content(self, obj):
        return (obj.content[:50] + "...") if len(obj.content) > 50 else obj.content

    short_content.short_description = "Сообщение"
