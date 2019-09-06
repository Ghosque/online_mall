import re

from django.conf import settings
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from django.core.cache import cache

from .serializers import MerchantRegSerializer, MerchantLoginSerializer, MerchantInfoSerializer, ShopRegSerializer,\
    CommoditySerializer
from .models import Merchant, Shop, BackStageSecond, Commodity, CommodityColor, Specification, SecondCategory
from common.models import MallUser
from common_function.get_id import GetId


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
            return Response(result, status=status.HTTP_200_OK)

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
            return Response(result, status=status.HTTP_200_OK)

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
            return Response(result, status=status.HTTP_200_OK)

        mall_user = MallUser.objects.get(phone=request.data['phone'])
        user = mall_user.user
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        cache.set(user.id, token, settings.REFRESH_SECONDS)

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
        """
        获取商家数据
        :param request:
        :param pk: user_id
        :return: code data(merchant_id name gender phone id_card token shop_name) message
        """
        token = re.search(settings.REGEX_TOKEN, request.environ.get('HTTP_AUTHORIZATION')).group(1)
        try:
            user = User.objects.get(id=pk)
            mall_user = MallUser.objects.get(user_id=user.id, is_merchant=1)

        except (User.DoesNotExist, MallUser.DoesNotExist):
            result = {
                'code': 0,
                'message': '查无此用户'
            }
            return Response(result, status=status.HTTP_200_OK)

        try:
            shop_name = mall_user.merchant.shop.name
        except Shop.DoesNotExist:
            shop_name = None
        data = {
            'user_id': pk,
            'token': token,
        }
        serializer = MerchantInfoSerializer(data=data)
        if not serializer.is_valid():
            result = {
                'code': 0,
                'data': None,
                'message': str(serializer.errors.get('token')[0])
            }
            return Response(result, status=status.HTTP_200_OK)

        result = {
            'code': 1,
            'data': {
                'merchant_id': mall_user.merchant.merchant_id,
                'name': mall_user.name,
                'gender': MallUser.GENDER_ITEMS[mall_user.gender][1],
                'phone': mall_user.phone,
                'id_card': mall_user.id_card,
                'token': token,
                'shop_name': shop_name,
                'shop_status': Shop.STATUS_ITEMS[mall_user.merchant.shop.status]
            },
            'message': '请求成功'
        }
        return Response(result, status=status.HTTP_200_OK)


class ShopInfoViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        """
        获取商店数据
        :param request:
        :param pk: user_id
        :return: code data(shop_id name star status token) message
        """
        token = re.search(settings.REGEX_TOKEN, request.environ.get('HTTP_AUTHORIZATION')).group(1)
        try:
            user = User.objects.get(id=pk)
            mall_user = MallUser.objects.get(user_id=user.id, is_merchant=1)

        except (User.DoesNotExist, MallUser.DoesNotExist):
            result = {
                'code': 0,
                'message': '查无此用户'
            }
            return Response(result, status=status.HTTP_200_OK)

        data = {
            'user_id': pk,
            'token': token,
        }
        serializer = MerchantInfoSerializer(data=data)
        if not serializer.is_valid():
            result = {
                'code': 0,
                'data': None,
                'message': str(serializer.errors.get('token')[0])
            }
            return Response(result, status=status.HTTP_200_OK)

        try:
            shop_id = mall_user.merchant.shop.shop_id
            shop_status = mall_user.merchant.shop.status
            result = {
                'code': 1,
                'data': {
                    'shop_id': shop_id,
                    'name': mall_user.merchant.shop.name,
                    'star': mall_user.merchant.shop.star,
                    'status': Shop.STATUS_ITEMS[shop_status][1],
                    'token': token,
                },
                'message': '请求成功'
            }
            return Response(result, status=status.HTTP_200_OK)

        except Shop.DoesNotExist:
            result = {
                'code': 2,
                'data': {},
                'message': '请求成功'
            }
            return Response(result, status=status.HTTP_200_OK)


class NavigationViewset(viewsets.ViewSet):

    def list(self, request):
        """
        获取导航栏
        :param request:
        :return: code data(back_stage_dict) message
        """
        back_stage_dict = BackStageSecond.get_back_stage_data()
        print(back_stage_dict)
        if not back_stage_dict:
            result = {
                'code': 0,
                'data': None,
                'message': '暂无导航栏数据'
            }
            return Response(result, status=status.HTTP_200_OK)

        result = {
            'code': 1,
            'data': back_stage_dict,
            'message': '请求成功'
        }
        return Response(result, status=status.HTTP_200_OK)


class CommodityViewset(viewsets.ViewSet):

    def create(self, request):
        """
        新增商品
        :param request: title title_desc cover inventory commodity_class, information
        :return:
        """
        serializer = CommoditySerializer(data=request.data)
        if not serializer.is_valid():
            pass

        token = re.search(settings.REGEX_TOKEN, request.environ.get('HTTP_AUTHORIZATION')).group(1)
        token_info = jwt_decode_handler(token)
        user_id = token_info['user_id']
        user = User.objects.get(pk=user_id)

        commodity_id = GetId.getDigitId()
        while Commodity.objects.filter(commodity_id=commodity_id):
            commodity_id = GetId.getDigitId()

        url = '47.107.183.166:9000/'

        category = SecondCategory.objects.get(id=serializer.validated_data['category'])

        commodity = Commodity.objects.create(
            commodity_id=commodity_id,
            title=serializer.validated_data['title'],
            title_desc=serializer.validated_data['title_desc'],
            url=url,
            cover=serializer.validated_data['cover'],
            inventory=serializer.validated_data['inventory'],
            category=category,
            shop=user.mall_user.merchant.shop,
        )

    def list(self, request):
        """
        商品列表
        :param request:
        :return:
        """
        pass

    def retrieve(self, request):
        """
        商品详情
        :param request:
        :return:
        """
        pass

    def update(self, request):
        """
        更新商品数据
        :param request:
        :return:
        """
        pass

    def destroy(self, request):
        """
        删除商品
        :param request:
        :return:
        """
        pass
