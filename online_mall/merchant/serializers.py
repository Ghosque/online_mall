from django.contrib.auth.models import User
from rest_framework import serializers
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from django.core.cache import cache

from .models import Merchant
from common.models import MallUser
from common.models import VerifyCode


class MerchantRegCodeSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True, max_length=500, label='密码', help_text="密码")
    name = serializers.CharField(required=True, write_only=True, max_length=50, label="姓名",
                                 error_messages={
                                     "max_length": "姓名格式错误",
                                 },
                                 help_text="姓名")
    gender = serializers.IntegerField(required=True, write_only=True, max_value=2, min_value=0, label="性别", help_text="性别")
    phone = serializers.CharField(required=True, write_only=True, max_length=11, label='手机号码',
                                  error_messages={
                                      "max_length": "手机号码格式错误",
                                      "min_length": "手机号码格式错误"
                                  },
                                  help_text="手机号码")
    id_card = serializers.CharField(required=True, write_only=True, max_length=18, min_length=18, label='身份证号码',
                                    error_messages={
                                        "max_length": "身份证号码格式错误",
                                        "min_length": "身份证号码格式错误"
                                    },
                                    help_text="身份证号码")
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                 error_messages={
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")

    def validate_id_card(self, id_card):
        # 检查最后一位校验码是否正确
        front_17_list = [i for i in id_card[:-1]]
        remainder = sum([int(i)*int(j) for i, j in zip(front_17_list, settings.COEFFICIENT_LIST)]) % 11
        if not settings.REMAINDER_DICT.get(remainder) == id_card[-1]:
            raise serializers.ValidationError("身份证错误")

        merchant_info = MallUser.objects.filter(id_card=id_card)
        if merchant_info:
            raise serializers.ValidationError("该身份证已被注册")

    def validate_code(self, code):
        # 前端传过来的所有的数据都在, initial_data 字典里面, 如果是验证通过的数据则保存在 validated_data 字典中
        verify_records = VerifyCode.objects.filter(phone=self.initial_data["phone"]).order_by("-update_time")
        if verify_records:
            last_record = verify_records[0]  # 时间倒叙排序后的的第一条就是最新的一条
            # 当前时间回退5分钟
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            # 最后一条短信记录的发出时间小于5分钟前, 表示是5分钟前发送的, 表示过期
            if five_mintes_ago > last_record.update_time:
                raise serializers.ValidationError("验证码过期")
            # 根据记录的 验证码 比对判断
            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")
            # return code  # 没必要保存验证码记录, 仅仅是用作验证
        else:
            raise serializers.ValidationError("验证码错误")

    class Meta:
        model = Merchant
        fields = ('password', 'name', 'gender', 'phone', 'id_card', 'code')


class MerchantLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, write_only=True, max_length=11, label='手机号码',
                                  error_messages={
                                      "max_length": "手机号码格式错误",
                                      "min_length": "手机号码格式错误"
                                  },
                                  help_text="手机号码")
    password = serializers.CharField(required=True, write_only=True, max_length=500, label='密码', help_text="密码")

    def validate_password(self, password):
        MallUser_list = MallUser.objects.filter(phone=self.initial_data["phone"], is_merchant=1)
        if MallUser_list:
            mall_user = MallUser_list[0]
            username = mall_user.user.username
            if not authenticate(username=username,password=password):
                raise serializers.ValidationError("密码错误")
            else:
                return mall_user.user


class MerchantInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, max_length=50, label="姓名")
    gender = serializers.IntegerField(required=True, max_value=2, min_value=0, label="性别")
    phone = serializers.CharField(required=True, max_length=11, label='手机号码')
    id_card = serializers.CharField(required=True, max_length=18, min_length=18, label='身份证号码')
    token = serializers.CharField(required=True, label="token", help_text="token")
    shop_name = serializers.CharField(required=True, allow_blank=True, allow_null=True, label='商店名称')

    def validate_token(self, token):
        token_info = jwt_decode_handler(token)
        user_id = token_info['user_id']
        expire_date = datetime.fromtimestamp(token_info['exp'])
        if settings.EXPIRE_SECONDS < (expire_date - datetime.now()).seconds < settings.REFRESH_SECONDS:
            user = User.objects.get(pk=user_id)
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

        return token

    class Meta:
        model = Merchant
        fields = ('name', 'gender', 'phone', 'id_card', 'token', 'shop_name')
