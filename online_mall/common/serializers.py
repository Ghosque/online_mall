from rest_framework import serializers
from django.conf import settings
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
