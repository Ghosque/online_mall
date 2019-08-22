from django.contrib.auth.models import User
from jwt.exceptions import ExpiredSignatureError
from rest_framework import serializers
from django.conf import settings
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from django.core.cache import cache
import re

from .models import MallUser


# 手机验证码序列化组件
class PhoneCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15, label='手机号码', help_text='手机号码')

    # 验证手机号码
    # validate_ + 字段名 的格式命名
    def validate_phone(self, phone):

        # 手机是否注册
        if MallUser.objects.filter(phone=phone).count():
            raise serializers.ValidationError("用户已经存在")

        # 验证手机号码是否合法
        if not re.match(settings.REGEX_PHONE, phone):
            raise serializers.ValidationError("手机号码非法")

        return phone


# 验证Token是否过期，若过期且在安全期内则返回新的Token
class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=True)

    def validate_token(self, token):
        try:
            token_info = jwt_decode_handler(token)
            user_id = token_info['user_id']
            if user_id != int(self.initial_data['user_id']):
                raise serializers.ValidationError("Token认证失败，请重新登录")

        except ExpiredSignatureError:
            if cache.get(self.initial_data['user_id']) and cache.get(self.initial_data['user_id']) == token:
                user = User.objects.get(pk=self.initial_data['user_id'])
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                cache.set(self.initial_data['user_id'], token, settings.REFRESH_SECONDS)
            else:
                raise serializers.ValidationError("Token过期，请重新登录")

        return token
