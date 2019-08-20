import re

from django.conf import settings
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from django.core.cache import cache

from .serializers import MerchantRegCodeSerializer, MerchantLoginSerializer, MerchantInfoSerializer
from .models import Merchant, Shop
from common.models import MallUser
from common_function import GetId


class MerchantRegViewset(viewsets.ViewSet):

    @classmethod
    def get_merchant_id(cls):
        merchant_id = GetId.getId()
        while User.objects.filter(username=merchant_id):
            merchant_id = GetId.getId()

        return merchant_id

    def create(self, request):
        """
        注册请求
        :param request: password name gender phone id_card code
        :return: code message
        """
        serializer = MerchantRegCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        merchant_id = self.get_merchant_id()

        user = User.objects.create_user(username=merchant_id, password=request.data['password'], is_superuser=0, is_staff=1)

        mall_user = MallUser.objects.create(
            name=request.data['name'],
            gender=request.data['gender'],
            phone=request.data['phone'],
            id_card=request.data['id_card'],
            is_merchant=1,
            user=user
        )
        Merchant.objects.create(mall_user=mall_user)

        result = {
            'code': 1,
            'message': '注册成功'
        }
        return Response(result, status=status.HTTP_201_CREATED)


class MerchantLoginViewset(viewsets.ViewSet):

    def create(self, request):
        """
        登录请求
        :param request: phone password
        :return: token user_id
        """
        serializer = MerchantLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mall_user = MallUser.objects.get(phone=request.data['phone'])
        user = mall_user.user
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        cache.set('token', token, settings.REFRESH_SECONDS)

        result = {
            'code': 1,
            'data': {
                'token': token,
                'user_id': user.id
            },
            'message': '登录成功'
        }
        return Response(result, status=status.HTTP_200_OK)


class MerchantInfoViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        token = re.search(settings.REGEX_TOKEN, request.environ.get('HTTP_AUTHORIZATION')).group(1)
        try:
            user = User.objects.get(id=pk)
            mall_user = MallUser.objects.get(user_id=user.id)
        except (User.DoesNotExist, MallUser.DoesNotExist):
            result = {
                'code': 0,
                'message': '查无此用户'
            }
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        try:
            shop_name = mall_user.merchant.shop.name
        except Shop.DoesNotExist:
            shop_name = None
        data = {
            'name': mall_user.name,
            'gender': mall_user.gender,
            'phone': mall_user.phone,
            'id_card': mall_user.id_card,
            'token': token,
            'shop_name': shop_name
        }
        print(data)
        serializer = MerchantInfoSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)
