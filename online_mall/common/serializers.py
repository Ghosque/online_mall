from django.contrib.auth.models import User
from rest_framework import serializers
from django.conf import settings
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
import re
from datetime import datetime, timedelta

from .models import MallUser, VerifyCode


# 手机验证码序列化组件
class PhoneCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)

    # 验证手机号码
    # validate_ + 字段名 的格式命名
    def validate_phone(self, phone):

        # 手机是否注册
        if MallUser.objects.filter(phone=phone).count():
            raise serializers.ValidationError("用户已经存在")

        # 验证手机号码是否合法
        if not re.match(settings.REGEX_PHONE, phone):
            raise serializers.ValidationError("手机号码非法")

        # 验证码发送频率
        # 当前时间减去一分钟(倒退一分钟), 然后发送时间要大于这个时间, 表示还在一分钟内
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(update_time__gt=one_mintes_ago, phone=phone).count():
            raise serializers.ValidationError("距离上一次发送未超过60s")

        return phone


# 验证Token是否过期，若过期且在安全期内则返回新的Token
class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def validate_token(self, token):
        token_info = jwt_decode_handler(token)
        user_id = token_info['user_id']
        expire_date = datetime.fromtimestamp(token_info['exp'])
        created_date = expire_date - timedelta(seconds=settings.EXPIRE_SECONDS)
        refresh_date = created_date + timedelta(seconds=settings.REFRESH_SECONDS)

        if datetime.now() < expire_date:
            pass

        elif datetime.now() < refresh_date:
            user = User.objects.get(pk=user_id)
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

        else:
            raise serializers.ValidationError("Token过期，请重新登录")

        return token
