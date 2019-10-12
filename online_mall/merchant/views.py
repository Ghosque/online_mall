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
from rest_framework.decorators import permission_classes
from django.core.cache import cache

from .serializers import MerchantRegSerializer, MerchantLoginSerializer, MerchantInfoSerializer, ShopRegSerializer
from .models import Merchant, Shop, BackStageSecond, Commodity, FirstCategory, SecondCategory, ThirdCategory,\
    MerchantImage, CommodityColor, Specification
from common.models import MallUser
from common_function.get_id import GetId


class MerchantViewset(viewsets.ViewSet):

    def create(self, request):
        type = request.GET.get('type')

        if type == 'login':
            result = self.handle_login(request)

        elif type == 'register':
            result = self.handle_register(request)

        else:
            result = {
                'code': 0,
                'data': None,
                'message': '类型错误'
            }

        return Response(result, status=status.HTTP_200_OK)

    @permission_classes([IsAuthenticated])
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

    @classmethod
    def handle_login(cls, request):
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

        return result

    @classmethod
    def get_merchant_id(cls):
        merchant_id = GetId.getId()
        while User.objects.filter(username=merchant_id):
            merchant_id = GetId.getId()

        return merchant_id

    @classmethod
    def handle_register(cls, request):
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

        merchant_id = cls.get_merchant_id()

        user = User.objects.create_user(username=merchant_id, password=request.data['password'], is_superuser=0,
                                        is_staff=1)

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

        return result


class ShopViewset(viewsets.ViewSet):

    def create(self, request):
        """
        注册商店
        :param request: name user_id
        :return: code data message
        """
        type = request.GET.get('type')

        if type == 'create':
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

        else:
            result = {
                'code': 1,
                'data': None,
                'message': '类型错误'
            }

        return Response(result, status=status.HTTP_200_OK)

    @permission_classes([IsAuthenticated])
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

    def retrieve(self, request, pk):
        type = request.GET.get('type')

        if type == '1':
            data = FirstCategory.get_point_category(pk)
            result = {
                'code': 1,
                'data': data,
                'message': '请求成功'
            }

        elif type == '2':
            data = SecondCategory.get_point_category(pk)
            result = {
                'code': 1,
                'data': data,
                'message': '请求成功'
            }

        elif type == '3':
            data = ThirdCategory.get_point_category(pk)
            result = {
                'code': 1,
                'data': data,
                'message': '请求成功'
            }

        else:
            data = None
            result = {
                'code': 0,
                'data': data,
                'message': '不存在该级分类'
            }

        return Response(result, status=status.HTTP_200_OK)


class ImageViewset(viewsets.ViewSet):

    def create(self, request):
        base64_data = request.data['base64_img']
        user_id = request.data['user_id']
        img_name = request.data['img_name']
        type = request.data['img_type']

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

                image_url = MerchantImage.upload_image(img, img_file)

                merchant_image_obj = MerchantImage.objects.create(
                    name=name,
                    oss_object=img,
                    img=image_url,
                    img_type=type,
                    merchant=merchant
                )

                result = {
                    'code': 1,
                    'data': {
                        'id': merchant_image_obj.id,
                        'img': merchant_image_obj.img,
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
            img_type = request.GET.get('img_type')
            img_list = MerchantImage.get_point_merchant_images(pk, img_type)

            result = {
                'code': 1,
                'data': img_list,
                'message': '请求成功'
            }

        return Response(result, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
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
        cover = self.save_base64_image(request.data['cover'], user_id, 'cover')
        # 分类
        category = ThirdCategory.objects.get(id=request.data['category'])
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
                    display_images=request.data['display_images'],
                    inventory=int(float(request.data['inventory'])),
                    price=float(request.data['price']),
                    category=category,
                    shop=user.mall_user.merchant.shop,
                )
                # 插入 CommodityColor 数据
                CommodityColor.objects.create(
                    commodity_class=json.dumps(request.data['color_item'], ensure_ascii=False),
                    commodity=commodity,
                )
                # 插入 Specification 数据
                Specification.objects.create(
                    information=json.dumps(attribute_item, ensure_ascii=False),
                    commodity=commodity,
                )
        except Exception as e:
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
        token = re.search(settings.REGEX_TOKEN, request.environ.get('HTTP_AUTHORIZATION')).group(1)
        token_info = jwt_decode_handler(token)
        user_id = token_info['user_id']
        commodity_status = int(request.GET.get('commodity_status'))
        if commodity_status not in [settings.COMMODITY_NORMAL_STATUS, settings.COMMODITY_IN_REVIEW_STATUS, settings.COMMODITY_OFF_SHELF_STATUS]:
            result = {
                'code': 0,
                'data': None,
                'message': '类型错误'
            }

        else:
            data_list = []
            # 获取目标status的商品列表
            commodity_list = Commodity.get_commodity(user_id, commodity_status)
            for item in commodity_list:
                # 获取颜色分类
                color_obj = CommodityColor.get_appoint_color(item)
                # 获取自定义属性
                specification_obj = Specification.get_point_spectification(item)

                single_data = {
                    'id': item.id,
                    'name': item.name,
                    'title': item.title,
                    'title_desc': item.title_desc,
                    'cover': item.cover,
                    'display_images': item.display_images,
                    'inventory': item.inventory,
                    'price': item.price,
                    'category': item.category.id,
                    'category_name': item.category.name,
                    'color_item': color_obj.commodity_class,
                    'attribute_item': specification_obj.information,
                }

                data_list.append(single_data)

            result = {
                'code': 1,
                'data': data_list,
                'message': '请求成功'
            }

        return Response(result, status=status.HTTP_200_OK)

    def retrieve(self, request):
        """
        商品详情
        :param request:
        :return:
        """
        pass

    def update(self, request, pk):
        """
        更新商品数据
        :param request:
        :return:
        """
        try:
            commodity = Commodity.get_appoint_commodity(pk)
            data = request.data
            with transaction.atomic():
                # 单独取出颜色分类
                if 'color_item' in data.keys():
                    color_item = data['color_item']
                    commodity_color_obj = CommodityColor.objects.filter(commodity=commodity)
                    commodity_color_obj.commodity_class = color_item
                    commodity_color_obj.save()

                    del data['color_item']
                # 单独取出自定义属性
                if 'attribute_item' in data.keys():
                    attribute_item = data['attribute_item']
                    specification_obj = Specification.objects.filter(commodity=commodity)
                    specification_obj.information = attribute_item
                    specification_obj.save()

                    del data['attribute_item']

                # 封面需要与原封面的base64数据进行对比
                if 'cover' in data.keys():
                    cover = data['cover']

                    original_cover = commodity.cover
                    base64_data = MerchantImage.get_image_base64_data(original_cover)
                    if base64_data == cover:
                        del data['cover']
                    else:
                        cover_url = self.save_base64_image(base64_data, commodity.merchant.mall_user.user.id, 'cover')
                        data['cover'] = cover_url

                # 商品类别作为外键需要进一步处理
                if 'category' in data.keys():
                    category = data['category']
                    category_object = ThirdCategory.objects.get(pk=category[-1])
                    data['category'] = category_object

                if data:
                    commodity.__dict__.update(**data)
                    commodity.save()

                result = {
                    'code': 1,
                    'data': None,
                    'message': '请求成功'
                }

        except Exception as e:
            print(str(e))
            result = {
                'code': 1,
                'data': None,
                'message': '没有该商品'
            }

        return Response(result, status=status.HTTP_200_OK)

    def destroy(self, request):
        """
        删除商品
        :param request:
        :return:
        """
        pass

    @classmethod
    def save_base64_image(cls, base64_img, user_id, type):
        if type == 'cover':
            img_type = 0
        else:
            img_type = 1

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

        image_url = MerchantImage.upload_image(img, img_file)

        MerchantImage.objects.create(
            name=name,
            oss_object=img,
            img=image_url,
            img_type=img_type,
            merchant=merchant
        )

        return image_url
