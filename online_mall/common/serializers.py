from django.contrib.auth.models import User
from jwt.exceptions import ExpiredSignatureError
from rest_framework import serializers
from django.conf import settings
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from django.core.cache import cache


# 验证Token是否过期，若过期且在安全期内则返回新的Token
class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=True)

    def validate_user_id(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("无此用户，请重新登录")

        else:
            return user_id

    def validate_token(self, token):
        try:
            token_info = jwt_decode_handler(token)
            user_id = token_info['user_id']
            if user_id != int(self.initial_data['user_id']):
                raise serializers.ValidationError("Token认证失败，请重新登录")

        except ExpiredSignatureError:
            key = 'user:token:'+str(self.initial_data['user_id'])
            if cache.get(key) and cache.get(key) == token:
                user = User.objects.get(pk=self.initial_data['user_id'])
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                cache.set(key, token, settings.REFRESH_SECONDS)
            else:
                raise serializers.ValidationError("Token过期，请重新登录")

        return token
