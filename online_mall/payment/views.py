import json

from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from common.models import Commodity, CommodityColor, SecondColorSelector
from merchant.models import MerchantImage
from common_function.django_redis_cache import Redis
from common_function.get_buyer_id import get_buyer_id

cache = Redis('default')


class ShoppingCartViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)

    def create(self, request):
        # 商品id colorItem_index 个数
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        id = request.data.get('id')
        item_index = request.data.get('item_index')
        num = request.data.get('num')
        cache_key = 'user:cart:{}'.format(buyer_id)
        if cache.hget(cache_key, '{}:{}'.format(id, item_index)):
            cache.hincrby(cache_key, '{}:{}'.format(id, item_index), num)
        else:
            cache.hset(cache_key, '{}:{}'.format(id, item_index), num)

        result = {
            'code': 1,
            'data': None,
            'message': '购物车数据新增成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def list(self, request):
        # 商品id 商品封面 标题 colorItem colorItem_index 单价 个数 商家店铺名
        data_list = list()

        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        cache_key = 'user:cart:{}'.format(buyer_id)
        data_dict = cache.hgetall(cache_key)
        for key, value in data_dict.items():
            id, item_index  = key.split(':')
            commodity = Commodity.get_appoint_commodity(int(id))
            # 获取颜色分类
            color_obj = CommodityColor.get_appoint_color(commodity)

            single_data = {
                'id': commodity.id,
                'name': commodity.name,
                'title': commodity.title,
                'title_desc': commodity.title_desc,
                'cover': commodity.cover,
                'price': commodity.price,
                'category': commodity.category.id,
                'category_name': commodity.category.name,
                'color_item': color_obj.commodity_class,
                'shop': commodity.shop.name,
                'item_index': int(item_index),
                'num': int(value)
            }

            # 处理颜色分类数据
            single_data['color_item'] = json.loads(single_data['color_item'])
            for index, color_item in enumerate(single_data['color_item']):
                single_data['color_item'][index]['color'] = SecondColorSelector.get_point_color(color_item['color'][1])
                single_data['color_item'][index]['img'] = MerchantImage.get_image_img(color_item['img'])

            data_list.insert(0, single_data)

        result = {
            'code': 1,
            'data': data_list,
            'message': '购物车数据获取成功'
        }

        return Response(result, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        # 商品id colorItem_index 个数
        item_index = request.data.get('item_index')
        num = request.data.get('num')
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        cache_key = 'user:cart:{}'.format(buyer_id)
        cache.hset(cache_key, '{}:{}'.format(pk, item_index), num)

        result = {
            'code': 1,
            'data': None,
            'message': '购物车数据修改成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        item_index = request.data.get('item_index')
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        cache_key = 'user:cart:{}'.format(buyer_id)
        cache.hdel(cache_key, '{}:{}'.format(pk, item_index))

        result = {
            'code': 1,
            'data': None,
            'message': '购物车数据删除成功'
        }

        return Response(result, status=status.HTTP_200_OK)
