import os
import re
import json
import base64
import random
import string

from django.conf import settings
from django.db import transaction
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from django.core.cache import cache

from .serializers import MerchantRegSerializer, MerchantLoginSerializer, MerchantInfoSerializer, ShopRegSerializer
from .models import Merchant, Shop, BackStageSecond, Commodity, FirstCategory, SecondCategory, ThirdCategory,\
    MerchantImage, CommodityColor, Specification
from common.models import MallUser, FirstColorSelector, SecondColorSelector
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
            shop_status = Shop.STATUS_ITEMS[mall_user.merchant.shop.status][1]
        except (Shop.DoesNotExist):
            shop_name = None
            shop_status = None
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
                'shop_status': shop_status
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


class CategoryViewset(viewsets.ViewSet):

    def list(self, request):
        """
        获取分类信息
        :param request:
        :return: code data(category_list) message
        """
        categoty_list = ThirdCategory.get_category()
        if not categoty_list:
            result = {
                'code': 0,
                'data': None,
                'message': '暂无导航栏数据'
            }

        else:
            result = {
                'code': 1,
                'data': categoty_list,
                'message': '请求成功'
            }

        return Response(result, status=status.HTTP_200_OK)


class FirstCategoryViewset(viewsets.ViewSet):

    def retrieve(self, request, pk):
        data = FirstCategory.get_point_category(pk)

        result = {
            'code': 1,
            'data': data,
            'message': '请求成功'
        }

        return Response(result, status=status.HTTP_200_OK)


class SecondCategoryViewset(viewsets.ViewSet):

    def retrieve(self, request, pk):
        data = SecondCategory.get_point_category(pk)

        result = {
            'code': 1,
            'data': data,
            'message': '请求成功'
        }

        return Response(result, status=status.HTTP_200_OK)


class ThirdCategoryViewset(viewsets.ViewSet):

    def retrieve(self, request, pk):
        data = ThirdCategory.get_point_category(pk)

        result = {
            'code': 1,
            'data': data,
            'message': '请求成功'
        }

        return Response(result, status=status.HTTP_200_OK)


class ImageUploadViewset(viewsets.ViewSet):

    def create(self, request):
        base64_data = request.data['base64_img']
        user_id = request.data['user_id']
        img_name = request.data['img_name']

        if not base64_data:
            result = {
                'code': 0,
                'data': None,
                'message': '上传图片为空'
            }

        else:
            new_base64_data = base64_data.split(',')[1]
            name = MerchantImage.get_name(img_name, user_id)
            img_dir = os.path.join(settings.MEDIA_ROOT, 'commodity', user_id)
            img_file = os.path.join(settings.MEDIA_ROOT, 'commodity', name)
            img = 'media/commodity/{}'.format(name)

            try:
                user = User.objects.get(pk=user_id)
                merchant = user.mall_user.merchant

            except (User.DoesNotExist, Merchant.DoesNotExist):
                result = {
                    'code': 2,
                    'data': None,
                    'message': '用户不存在'
                }

            else:
                img_data = base64.b64decode(new_base64_data)
                if not os.path.isdir(img_dir):
                    os.makedirs(img_dir)

                with open(img_file, 'ab') as f:
                    f.write(img_data)

                merchant_image_obj = MerchantImage.objects.create(
                    name=name,
                    img=img,
                    merchant=merchant
                )

                result = {
                    'code': 1,
                    'data': {
                        'id': merchant_image_obj.id,
                        'img': MerchantImage.img_covert_base64(os.path.join(settings.BASE_DIR, merchant_image_obj.img)),
                    },
                    'message': '上传成功'
                }

        return Response(result, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        try:
            User.objects.get(pk=pk)

        except User.DoesNotExist:
            result = {
                'code': 0,
                'data': None,
                'message': '用户不存在'
            }

        else:
            img_list = MerchantImage.get_point_merchant_images(pk)

            result = {
                'code': 1,
                'data': img_list,
                'message': '请求成功'
            }

        return Response(result, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        print(pk)
        delete_list = request.data['delete_list']
        MerchantImage.delete_images(delete_list)

        result = {
            'code': 1,
            'data': None,
            'message': '删除成功'
        }

        return Response(result, status=status.HTTP_200_OK)


class CommodityViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)

    def create(self, request):
        """
        新增商品
        :param request: title title_desc cover inventory commodity_class, information
        :return:
        """
        token = re.search(settings.REGEX_TOKEN, request.environ.get('HTTP_AUTHORIZATION')).group(1)
        token_info = jwt_decode_handler(token)
        user_id = token_info['user_id']
        user = User.objects.get(pk=user_id)

        # 商品ID
        commodity_id = GetId.getDigitId()
        while Commodity.objects.filter(commodity_id=commodity_id):
            commodity_id = GetId.getDigitId()
        # 封面
        cover = self.saveBase64Image(request.data['cover'], user_id, 'cover')
        # 展示图片
        display_image_list = []
        for image in request.data['display_images']:
            new = self.saveBase64Image(image, user_id, 'imagePicture')
            display_image_list.append(new)
        # 分类
        category = ThirdCategory.objects.get(id=request.data['category'])

        # 颜色分类
        color_item = request.data['color_item']
        for item in color_item:
            color_list = item['color']
            item['color'][0] = FirstColorSelector.get_point_color(color_list[0])
            item['color'][1] = SecondColorSelector.get_point_color(color_list[1])

        # 自定义属性
        attribute_item = request.data['attribute_item']

        try:
            with transaction.atomic():
                # 插入 Commodity 数据
                commodity = Commodity.objects.create(
                    commodity_id=commodity_id,
                    name=request.data['name'],
                    title=request.data['title'],
                    title_desc=request.data['title_desc'],
                    cover=cover,
                    display_images=display_image_list,
                    inventory=int(float(request.data['inventory'])),
                    price=float(request.data['price']),
                    category=category,
                    shop=user.mall_user.merchant.shop,
                )
                # 插入 CommodityColor 数据
                CommodityColor.objects.create(
                    commodity_class=json.dumps(color_item, ensure_ascii=False),
                    commodity=commodity,
                )
                # 插入 Specification 数据
                Specification.objects.create(
                    information=json.dumps(attribute_item, ensure_ascii=False),
                    commodity=commodity,
                )
        except Exception as e:
            print(e)
            result = {
                'code': 0,
                'data': None,
                'msssage': '上传失败'
            }
        else:
            result = {
                'code': 1,
                'data': None,
                'msssage': '上传成功'
            }

        return Response(result, status=status.HTTP_200_OK)

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

    def saveBase64Image(cls, base64_img, user_id, type):
        base64_img = base64_img.split(',')[1]
        img_name = ''.join(random.sample(string.ascii_letters + string.digits, 8)) + '.jpg'
        name = MerchantImage.get_name(img_name, str(user_id))
        img_dir = os.path.join(settings.MEDIA_ROOT, type, str(user_id))
        img_file = os.path.join(settings.MEDIA_ROOT, type, name)
        img = 'media/{}/{}'.format(type, name)

        user = User.objects.get(pk=user_id)
        merchant = user.mall_user.merchant

        img_data = base64.b64decode(base64_img)
        if not os.path.isdir(img_dir):
            os.makedirs(img_dir)

        with open(img_file, 'ab') as f:
            f.write(img_data)

        MerchantImage.objects.create(
            name=name,
            img=img,
            merchant=merchant
        )

        return img
