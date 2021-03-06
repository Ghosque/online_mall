import re
from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_jwt.utils import jwt_decode_handler

from .models import Merchant, Shop
from common_function.django_redis_cache import Redis

cache = Redis('default')


class MerchantRegSerializer(serializers.Serializer):
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
    code_key = serializers.CharField(required=True, write_only=True, label='验证码key', help_text='验证码key')
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                 error_messages={
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")

    # 验证手机号码
    # validate_ + 字段名 的格式命名
    def validate_phone(self, phone):

        # 手机是否注册
        if Merchant.objects.filter(phone=phone).count():
            raise serializers.ValidationError("用户已经存在")

        # 验证手机号码是否合法
        if not re.match(settings.REGEX_PHONE, phone):
            raise serializers.ValidationError("手机号码非法")

        return phone

    def validate_id_card(self, id_card):
        # 检查最后一位校验码是否正确
        front_17_list = [i for i in id_card[:-1]]
        remainder = sum([int(i)*int(j) for i, j in zip(front_17_list, settings.COEFFICIENT_LIST)]) % 11
        if not settings.REMAINDER_DICT.get(remainder) == id_card[-1]:
            raise serializers.ValidationError("身份证错误")

        merchant_info = Merchant.objects.filter(id_card=id_card)
        if merchant_info:
            raise serializers.ValidationError("该身份证已被注册")

    def validate_code(self, code):
        key = 'merchant:code:'+self.initial_data['code_key']
        if not cache.get(key):
            raise serializers.ValidationError("该验证码已过期，请重新获取")

        true_code = cache.get(key)
        if true_code.lower() != code.lower():
            raise serializers.ValidationError("验证码错误")

    class Meta:
        model = Merchant
        fields = ('password', 'name', 'gender', 'phone', 'id_card', 'code_key', 'code')


class ShopRegSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True, write_only=True, label='用户ID', help_text='用户ID')
    name = serializers.CharField(required=True, write_only=True, max_length=50, min_length=4, label='店名',
                                 error_messages={
                                     "max_length": "店名长度不能超过50个字节",
                                     "min_length": "店名长度不能少于10个字节"
                                 },
                                 help_text="店名")

    def validate_name(self, name):
        name_list = Shop.objects.filter(name=name)
        if name_list:
            raise serializers.ValidationError("该店名正在审核中或已被注册")


class MerchantLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, write_only=True, max_length=11, label='手机号码',
                                  error_messages={
                                      "max_length": "手机号码格式错误",
                                      "min_length": "手机号码格式错误"
                                  },
                                  help_text="手机号码")
    password = serializers.CharField(required=True, write_only=True, max_length=500, label='密码', help_text="密码")

    def validate_password(self, password):
        Merchant_list = Merchant.objects.filter(phone=self.initial_data["phone"])
        if Merchant_list:
            mall_user = Merchant_list[0]
            username = mall_user.user.username
            if not authenticate(username=username, password=password):
                raise serializers.ValidationError("密码错误")
        else:
            raise serializers.ValidationError("手机号码错误")


class MerchantInfoSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True, label='用户ID', help_text='用户ID')
    token = serializers.CharField(required=True, label="token", help_text="token")

    def validate_token(self, token):
        token_info = jwt_decode_handler(token)
        user_id = token_info['user_id']
        print(self.initial_data)
        if user_id != int(self.initial_data['user_id']):
            raise serializers.ValidationError("Token认证失败，请重新登录")

        return token


class ShopInfoSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True, label='用户ID', help_text='用户ID')
    token = serializers.CharField(required=True, label="token", help_text="token")

    def validate_token(self, token):
        token_info = jwt_decode_handler(token)
        user_id = token_info['user_id']
        print(self.initial_data)
        if user_id != int(self.initial_data['user_id']):
            raise serializers.ValidationError("Token认证失败，请重新登录")

        return token
