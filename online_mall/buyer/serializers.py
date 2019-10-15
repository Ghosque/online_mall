from rest_framework import serializers

from .models import Buyer


class BuyerLoginSerializer(serializers.Serializer):
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
    code_key = serializers.CharField(required=True, write_only=True, label='验证码key', help_text='验证码key')
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                 error_messages={
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")
