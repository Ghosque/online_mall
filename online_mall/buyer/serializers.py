import re
from django.core.cache import cache
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import Buyer
from common.models import MallUser


class BuyerLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, write_only=True, max_length=11, label='手机号码',
                                  error_messages={
                                      "max_length": "手机号码格式错误",
                                      "min_length": "手机号码格式错误"
                                  },
                                  help_text="手机号码")
    password = serializers.CharField(required=True, write_only=True, max_length=500, label='密码', help_text="密码")

    def validate_password(self, password):
        MallUser_list = MallUser.objects.filter(phone=self.initial_data["phone"], is_merchant=0)
        if MallUser_list:
            mall_user = MallUser_list[0]
            username = mall_user.user.username
            if not authenticate(username=username, password=password):
                raise serializers.ValidationError("密码错误")
        else:
            raise serializers.ValidationError("手机号码错误")


class BuyerRegSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True, max_length=500, label='密码', help_text="密码")
    name = serializers.CharField(required=True, write_only=True, max_length=50, label="姓名",
                                 error_messages={
                                     "max_length": "姓名格式错误",
                                 },
                                 help_text="姓名")
    gender = serializers.IntegerField(required=True, write_only=True, max_value=2, min_value=0, label="性别",
                                      help_text="性别")
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
    nickname = serializers.CharField(required=True, write_only=True, max_length=30, label="昵称",
                                     error_messages={
                                         "max_length": "昵称格式错误",
                                     },
                                     help_text="昵称")
    code_key = serializers.CharField(required=True, write_only=True, label='验证码key', help_text='验证码key')
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                 error_messages={
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")

    # 验证手机号码
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
        remainder = sum([int(i) * int(j) for i, j in zip(front_17_list, settings.COEFFICIENT_LIST)]) % 11
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
        model = Buyer
        fields = ('password', 'name', 'gender', 'phone', 'id_card', 'code_key', 'code')
