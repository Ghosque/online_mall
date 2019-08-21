from rest_framework import viewsets, status
from rest_framework.response import Response
from random import choice

from .serializers import PhoneCodeSerializer, TokenVerifySerializer
from .models import VerifyCode


# 发送短信验证码
class PhoneCodeViewset(viewsets.ViewSet):

    # 生成四位数字的验证码
    def generate_code(self):

        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request):
        print(request.data)
        serializer = PhoneCodeSerializer(data=request.data)
        if not serializer.is_valid():
            result = {
                'code': 0,
                'data': None,
                'message': str(serializer.errors.get('phone')[0])
            }
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # 验证后即可取出数据
        phone = serializer.validated_data["phone"]
        code = self.generate_code()

        # 确认无误后需要保存数据库中
        code_record = VerifyCode(code=code, phone=phone)
        code_record.save()

        result = {
            'code': 1,
            'data': {
                'phone': phone,
                'verify_code': code
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
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        result = {
            'code': 1,
            'data': {
                'token': serializer.data['token'],
                'user_id': serializer.data['user_id']
            },
            'message': '请求成功'
        }
        return Response(result, status=status.HTTP_200_OK)
