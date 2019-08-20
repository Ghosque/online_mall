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
        serializer = PhoneCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 验证后即可取出数据
        phone = serializer.validated_data["phone"]
        code = self.generate_code()

        # 确认无误后需要保存数据库中
        code_record = VerifyCode(code=code, phone=phone)
        code_record.save()
        return Response({
            "phone": phone,
            "verify_code": code
        }, status=status.HTTP_201_CREATED)


class TokenVerifyViewset(viewsets.ViewSet):

    def create(self, request):
        serializer = PhoneCodeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'code': 0}, status=status.HTTP_400_BAD_REQUEST)
