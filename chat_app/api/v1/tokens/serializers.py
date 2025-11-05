from rest_framework import serializers


class TokensSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField(allow_null=True, required=False)
    token_type = serializers.CharField()


class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class TokenObtainPairParamsSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class TokensRefreshParamsSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
