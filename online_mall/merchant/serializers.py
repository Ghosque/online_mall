import re
from django.core.cache import cache
from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_jwt.utils import jwt_decode_handler

from .models import Merchant, Shop
from common.models import MallUser


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
        if MallUser.objects.filter(phone=phone).count():
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

        merchant_info = MallUser.objects.filter(id_card=id_card)
        if merchant_info:
            raise serializers.ValidationError("该身份证已被注册")

    def validate_code(self, code):
        if not cache.get(self.initial_data['code_key']):
            raise serializers.ValidationError("该验证码已过期，请重新获取")

        true_code = cache.get(self.initial_data['code_key'])
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
        MallUser_list = MallUser.objects.filter(phone=self.initial_data["phone"], is_merchant=1)
        if MallUser_list:
            mall_user = MallUser_list[0]
            username = mall_user.user.username
            if not authenticate(username=username,password=password):
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


class CommoditySerializer(serializers.Serializer):
    title = serializers.CharField(required=True, write_only=True, max_length=500, min_length=10, label='详情页标题',
                                  error_messages={
                                      "max_length": "超过长度限制",
                                      "min_length": "未达到长度标准"
                                  },
                                  help_text='详情页标题')
    title_desc = serializers.CharField(required=True, write_only=True, max_length=200, min_length=10, label='预览页标题',
                                       error_messages={
                                           "max_length": "超过长度限制",
                                           "min_length": "未达到长度标准"
                                       },
                                       help_text='预览页标题')
    cover = serializers.ImageField(required=True, write_only=True, label='封面', help_text='封面')
    inventory = serializers.IntegerField(required=True, write_only=True, max_value=9999, min_value=5, label='库存',
                                         error_messages={
                                           "max_value": "超过限制数量",
                                           "min_value": "未达标准数量"
                                         },
                                         help_text='库存')
    commodity_class = serializers.JSONField(required=True, write_only=True, label='分类', help_text='分类')
    information = serializers.JSONField(required=True, write_only=True, label='详情', help_text='详情')
    category = serializers.IntegerField(required=True, write_only=True, label='类别', help_text='类别')
