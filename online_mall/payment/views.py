import json

from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from common.models import Commodity
from common_function.django_redis_cache import Redis
from common_function.get_buyer_id import get_buyer_id

cache = Redis('default')


class ShoppingCartViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)

    def create(self, request):
        # 商品id colorItem_index 个数
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        data = {
            'id': request.data.get('id'),
            'item_index': request.data.get('item_index'),
            'number': request.data.get('number')
        }
        cache_key = 'user:cart:{}:{}'.format(buyer_id, request.data.get('id'))
        cache.set(cache_key, json.dumps(data), settings.APPLET_REFRESH_SECONDS)

        result = {
            'code': 1,
            'data': None,
            'message': '购物车新增数据成功'
        }

        return Response(result, status=status.HTTP_201_CREATED)

    def list(self, request):
        # 商品id 商品封面 标题 colorItem colorItem_index 单价 个数 商家店铺名
        data_list = list()

        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        cache_key_model = 'user:cart:{}:*'.format(buyer_id)
        keys = cache.keys(cache_key_model)
        for key in keys:
            single_dict = dict()
            data = eval(cache.get(key))
            id = data['id']
            item_index = data['item_index']
            number = data['number']

            commodity = Commodity.get_appoint_commodity(id)
            color_item = commodity.CommodityColor.commodity_class
            # TODO

        result = {
            'code': 1,
            'data': data_list,
            'message': '获取购物车数据成功'
        }

        return Response(result, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        # 商品id colorItem_index 个数
        pass

    def destroy(self, request, pk):
        pass
