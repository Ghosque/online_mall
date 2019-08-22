import re

from django.conf import settings
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from django.core.cache import cache

from .serializers import MerchantRegSerializer, MerchantLoginSerializer, MerchantInfoSerializer, ShopRegSerializer
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
        :return: code data message
        """
        serializer = MerchantRegSerializer(data=request.data)
        if not serializer.is_valid():
            if serializer.errors.get('id_card'):
                message = str(serializer.errors.get('id_card')[0])
            else:
                message = str(serializer.errors.get('code')[0])

            result = {
                'code': 0,
                'data': None,
                'message': message
            }
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

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
            'data': None,
            'message': '注册成功'
        }
        return Response(result, status=status.HTTP_201_CREATED)


class ShopRegViewset(viewsets.ViewSet):

    def create(self, request):
        """
        注册商店
        :param request: name user_id
        :return: code data message
        """
        serializer = ShopRegSerializer(data=request.data)
        if not serializer.is_valid():
            result = {
                'code': 0,
                'data': None,
                'message': str(serializer.errors.get('name')[0])
            }
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(pk=request.data['user_id'])
        merchant = user.mall_user.merchant
        Shop.objects.create(
            name=request.data['name'],
            merchant=merchant
        )

        result = {
            'code': 1,
            'data': None,
            'message': '商店登记成功'
        }
        return Response(result, status=status.HTTP_200_OK)


class MerchantLoginViewset(viewsets.ViewSet):

    def create(self, request):
        """
        登录请求
        :param request: phone password
        :return: code data(token user_id) message
        """
        serializer = MerchantLoginSerializer(data=request.data)
        if not serializer.is_valid():
            result = {
                'code': 0,
                'data': None,
                'message': str(serializer.errors.get('password')[0])
            }
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

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
            mall_user = MallUser.objects.get(user_id=user.id, is_merchant=1)

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
            'user_id': pk,
            'merchant_id': mall_user.merchant.merchant_id,
            'name': mall_user.name,
            'gender': mall_user.gender,
            'phone': mall_user.phone,
            'id_card': mall_user.id_card,
            'token': token,
            'shop_name': shop_name
        }
        print(data)
        serializer = MerchantInfoSerializer(data=data)
        if not serializer.is_valid():
            result = {
                'code': 0,
                'data': None,
                'message': str(serializer.errors.get('token')[0])
            }
            return Response(result, status=status.HTTP_403_FORBIDDEN)

        result = {
            'code': 1,
            'data': {
                'merchant_id': mall_user.merchant.merchant_id,
                'name': mall_user.name,
                'gender': mall_user.gender,
                'phone': mall_user.phone,
                'id_card': mall_user.id_card,
                'token': token,
                'shop_name': shop_name
            },
            'message': '请求成功'
        }
        return Response(result, status=status.HTTP_200_OK)


class ShopInfoViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        pass
