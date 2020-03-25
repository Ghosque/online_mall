import os
import re
import base64

from django.conf import settings
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from rest_framework.decorators import permission_classes

from .serializers import MerchantRegSerializer, MerchantLoginSerializer, MerchantInfoSerializer, ShopRegSerializer
from .models import Merchant, Shop, BackStageSecond, FirstCategory, SecondCategory, ThirdCategory, MerchantImage
from common_function.get_id import GetId
from common_function.django_redis_cache import Redis

cache = Redis('default')


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
            merchant = Merchant.objects.get(user_id=user.id)

        except (User.DoesNotExist, merchant.DoesNotExist):
            result = {
                'code': 0,
                'message': '查无此用户'
            }
            return Response(result, status=status.HTTP_200_OK)

        try:
            shop_name = merchant.shop.name
            shop_status = Shop.STATUS_ITEMS[merchant.shop.status][1]
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
                'merchant_id': merchant.merchant_id,
                'name': merchant.name,
                'gender': Merchant.GENDER_ITEMS[merchant.gender][1],
                'phone': merchant.phone,
                'id_card': merchant.id_card,
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

        merchant = Merchant.objects.get(phone=request.data['phone'])
        user = merchant.user
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        cache.set('merchant:token:'+str(user.id), token, settings.REFRESH_SECONDS)

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

        user = User.objects.create_user(
            username=merchant_id,
            password=request.data['password'],
            is_superuser=0,
            is_staff=1
        )

        Merchant.objects.create(
            merchant_id=merchant_id,
            name=request.data['name'],
            gender=request.data['gender'],
            phone=request.data['phone'],
            id_card=request.data['id_card'],
            user=user
        )

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
            merchant = user.merchant
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
            merchant = Merchant.objects.get(user_id=user.id)

        except (User.DoesNotExist, merchant.DoesNotExist):
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
            shop_id = merchant.shop.shop_id
            shop_status = merchant.shop.status
            result = {
                'code': 1,
                'data': {
                    'shop_id': shop_id,
                    'name': merchant.shop.name,
                    'star': merchant.shop.star,
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
                merchant = user.merchant

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
