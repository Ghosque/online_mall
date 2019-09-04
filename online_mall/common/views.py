import os

from django.conf import settings
from django.core.cache import cache
from rest_framework import viewsets, status
from rest_framework.response import Response

from random import choice
import string

from .serializers import TokenVerifySerializer
from common_function import get_verify_code


# 获取验证码图片
class PhoneCodeViewset(viewsets.ViewSet):

    # 生成四位的验证码key
    def generate_code_key(self):

        seeds = string.digits + string.ascii_uppercase
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def list(self, request):

        code_key = self.generate_code_key()
        while cache.get(code_key):
            code_key = self.generate_code_key()

        code_img, code = get_verify_code.gene_code(code_key)

        cache.set(code_key, code, settings.CODE_VALIDATION)

        result = {
            'code': 1,
            'data': {
                'code_key': code_key,
                'code_img': code_img
            },
            'message': '获取验证码成功'
        }
        return Response(result, status=status.HTTP_201_CREATED)


class TokenVerifyViewset(viewsets.ViewSet):

    def create(self, request):
        serializer = TokenVerifySerializer(data=request.data)
        if not serializer.is_valid():
            result = {
                'code': 0,
                'data': None,
                'message': str(serializer.errors.get('token')[0])
            }
            return Response(result, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)

        result = {
            'code': 1,
            'data': {
                'token': serializer.data['token'],
                'user_id': serializer.data['user_id']
            },
            'message': '请求成功'
        }
        return Response(result, status=status.HTTP_200_OK)
