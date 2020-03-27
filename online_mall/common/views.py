import os
import json
import base64
import random
import re

from django.conf import settings
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.utils import jwt_decode_handler

from random import choice
import string


from .models import SecondColorSelector, Commodity, CommodityColor, Specification, CardTicket, CommodityComment
from .serializers import TokenVerifySerializer
from common_function import get_verify_code
from common_function.get_id import GetId
from merchant.models import Merchant, Shop, BackStageSecond, FirstCategory, SecondCategory, ThirdCategory, MerchantImage
from buyer.models import Buyer
from common_function.django_redis_cache import Redis
from common_function.get_buyer_id import get_buyer_id
from common_function.get_timestamp import get_after_30_days_timestamp, get_today_timestamp

cache = Redis('default')


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
        while cache.get('merchant:code:'+code_key):
            code_key = self.generate_code_key()

        code_img, code = get_verify_code.gene_code(code_key)

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
        print(request.data)
        data = request.data
        type = data['type'] if 'type' in data.keys() else None
        data['type'] = type
        serializer = TokenVerifySerializer(data=data)
        if not serializer.is_valid():
            if serializer.errors.get('user_id'):
                message = str(serializer.errors.get('user_id')[0])
            else:
                message = str(serializer.errors.get('token')[0])

            result = {
                'code': 0,
                'data': None,
                'message': message
            }
        else:
            user_id = serializer.data['user_id']
            buyer_id = User.objects.get(pk=user_id).buyer.id
            result = {
                'code': 1,
                'data': {
                    'buyer_id': buyer_id,
                    'user_id': user_id,
                    'token': serializer.data['token']
                },
                'message': '请求成功'
            }

        return Response(result, status=status.HTTP_200_OK)


class ColorViewset(viewsets.ViewSet):

    def create(self, request):
        color = request.data['color']
        color_name = SecondColorSelector.get_point_color(color)

        result = {
            'code': 1,
            'data': color_name,
            'message': '请求成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def list(self, request):
        """
        获取颜色分类列表
        :param request:
        :return: code data(color_selector_list) message
        """
        color_selector_list = SecondColorSelector.get_color_selector()
        color_code_name_dict = SecondColorSelector.get_code_name_dict()
        if not color_selector_list:
            result = {
                'code': 0,
                'data': None,
                'message': '暂无颜色分类器数据'
            }
        else:
            result = {
                'code': 1,
                'data': {
                    'selector_list': color_selector_list,
                    'code_name_dict': color_code_name_dict,
                },
                'message': '请求成功'
            }

        return Response(result, status=status.HTTP_200_OK)


class CommodityViewset(viewsets.ViewSet):
    """
    商家商品接口
    """

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
                    shop=user.merchant.shop,
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
            # 获取目标status的商品列表
            commodity_list = Commodity.get_commodity(user_id, commodity_status)

            result = {
                'code': 1,
                'data': commodity_list,
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

                    original_cover = MerchantImage.get_image_oss_object(commodity.cover)
                    base64_data = MerchantImage.get_image_base64_data(original_cover)
                    if base64_data == cover:
                        del data['cover']
                    else:
                        cover = self.save_base64_image(cover, commodity.shop.merchant.user.id, 'cover')
                        data['cover'] = cover

                # 商品类别作为外键需要进一步处理
                if 'category' in data.keys():
                    category = data['category']
                    category_object = ThirdCategory.objects.get(pk=category[-1])
                    data['category'] = category_object

                if data:
                    print(data)
                    commodity.__dict__.update(**data)
                    commodity.save()

                result = {
                    'code': 1,
                    'data': None,
                    'message': '请求成功'
                }

        except Exception as e:
            result = {
                'code': 0,
                'data': None,
                'message': '没有该商品'
            }

        return Response(result, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        """
        删除商品
        :param request:
        :return:
        """
        delete_type = request.GET.get('delete_type')

        try:
            commodity_obj = Commodity.objects.get(id=pk)

            if delete_type == '1':
                commodity_obj.status = 3
                commodity_obj.save()

                result = {
                    'code': 1,
                    'data': None,
                    'message': '请求成功'
                }

            elif delete_type == '2':
                commodity_obj.status = 0
                commodity_obj.save()

                result = {
                    'code': 1,
                    'data': None,
                    'message': '请求成功'
                }

            elif delete_type == '3':
                commodity_obj.status = 2
                commodity_obj.save()

                result = {
                    'code': 1,
                    'data': None,
                    'message': '请求成功'
                }

            else:
                result = {
                    'code': 0,
                    'data': None,
                    'message': '类型错误'
                }

        except Commodity.DoesNotExist:
            result = {
                'code': 0,
                'data': None,
                'message': '没有该商品'
            }

        return Response(result, status=status.HTTP_200_OK)

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
        merchant = user.merchant

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


class BuyerCommodityViewset(viewsets.ViewSet):

    def list(self, request):
        type = request.GET.get('type')
        name = None

        if type == 'hot':
            commodity_list = Commodity.get_hot_commodity()
        else:
            commodity_list, name = Commodity.get_appoint_category_commodity(request.GET.get('category_id'))

        for i, commodity in enumerate(commodity_list):
            # 处理照片墙数据
            for index, image_id in enumerate(commodity['display_images']):
                commodity['display_images'][index] = MerchantImage.get_image_img(image_id)
            # 处理颜色分类数据
            commodity['color_item'] = json.loads(commodity['color_item'])
            for index, color_item in enumerate(commodity['color_item']):
                commodity['color_item'][index]['color'] = SecondColorSelector.get_point_color(color_item['color'][1])
                commodity['color_item'][index]['img'] = MerchantImage.get_image_img(color_item['img'])
            # 处理属性数据
            commodity['attribute_item'] = json.loads(commodity['attribute_item'])
            for index, attribute_item in enumerate(commodity['attribute_item']):
                commodity['attribute_item'][index] = {attribute_item['attribute']: attribute_item['content']}
            # 获取评价数据
            all_comments, good_rate = CommodityComment.get_data(commodity['id'])
            commodity_list[i]['comment_count'] = len(all_comments)
            commodity_list[i]['good_rate'] = good_rate

        result = {
            'code': 1,
            'data': commodity_list,
            'name': name,
            'message': '获取commodity成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        buyer_id = request.GET.get('buyer_id')

        commodity = Commodity.get_appoint_commodity(pk)
        # 获取颜色分类
        color_obj = CommodityColor.get_appoint_color(commodity)
        # 获取自定义属性
        specification_obj = Specification.get_point_spectification(commodity)
        # 获取评价数据
        all_comments, good_rate = CommodityComment.get_data(commodity.id)
        # 获取买家是否关注商品
        cache_key = 'user:follow:commodity:{}'.format(buyer_id)
        follow_list = cache.lrange(cache_key, 0, -1)
        if pk in follow_list:
            is_follow = True
        else:
            is_follow = False

        single_data = {
            'id': commodity.id,
            'name': commodity.name,
            'title': commodity.title,
            'title_desc': commodity.title_desc,
            'cover': commodity.cover,
            'display_images': commodity.display_images,
            'inventory': commodity.inventory,
            'price': commodity.price,
            'category': commodity.category.id,
            'category_name': commodity.category.name,
            'color_item': color_obj.commodity_class,
            'attribute_item': specification_obj.information,
            'shop': commodity.shop.name,
            'comments': all_comments,
            'good_rate': good_rate,
            'is_follow': is_follow
        }

        # 处理照片墙数据
        for index, image_id in enumerate(single_data['display_images']):
            single_data['display_images'][index] = MerchantImage.get_image_img(image_id)
        # 处理颜色分类数据
        single_data['color_item'] = json.loads(single_data['color_item'])
        for index, color_item in enumerate(single_data['color_item']):
            single_data['color_item'][index]['color'] = SecondColorSelector.get_point_color(color_item['color'][1])
            single_data['color_item'][index]['img'] = MerchantImage.get_image_img(color_item['img'])
        # 处理属性数据
        single_data['attribute_item'] = json.loads(single_data['attribute_item'])
        for index, attribute_item in enumerate(single_data['attribute_item']):
            single_data['attribute_item'][index] = {attribute_item['attribute']: attribute_item['content']}

        result = {
            'code': 1,
            'data': single_data,
            'message': '获取commodity成功'
        }

        return Response(result, status=status.HTTP_200_OK)


class CommodityFollowViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)
    cache_key_model = 'user:follow:commodity:{}'

    def create(self, request):
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        commodity_id = request.data.get('commodity_id')
        follow_status = request.data.get('follow_status')

        cache_key = self.cache_key_model.format(buyer_id)
        if follow_status:
            cache.lpush(cache_key, commodity_id)
        else:
            cache.lrem(cache_key, 0, commodity_id)

        result = {
            'code': 1
        }

        return Response(result, status=status.HTTP_200_OK)

    def list(self, request):
        buyer_id = request.GET.get('buyer_id')
        cache_key = self.cache_key_model.format(buyer_id)
        follow_list = cache.lrange(cache_key, 0, -1)
        print(follow_list)


class ShopFollowViewset(viewsets.ViewSet):
    pass


class BuyerTraceViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)
    cache_key_model = 'user:trace:{}'

    def create(self, request):
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        commodity_id = request.data.get('commodity_id')
        timestamp = get_after_30_days_timestamp()

        cache.zadd(self.cache_key_model.format(buyer_id), {commodity_id: timestamp})

        result = {
            'code': 1,
            'message': '记录浏览记录成功'
        }

        return Response(result, status=status.HTTP_200_OK)


class NoteViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)

    def list(self, request):
        type = request.GET.get('type')
        buyer_id = request.GET.get('buyer_id')

        buyer = Buyer.objects.get(pk=buyer_id)

        commodity_follow = cache.llen('user:follow:commodity:{}'.format(buyer_id))
        shop_follow = cache.llen('user:follow:shop:{}'.format(buyer_id))

        commodity_view = cache.zcard('user:trace:{}'.format(buyer_id))

        card = CardTicket.get_card(buyer, type)

        data = [commodity_follow, shop_follow, commodity_view, card]

        result = {
            'code': 1,
            'data': data,
            'message': '获取note成功'
        }

        return Response(result, status=status.HTTP_200_OK)
