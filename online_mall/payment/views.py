import json

from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Order, SinglePurchaseOrder
from common.models import Commodity, CommodityColor, SecondColorSelector
from merchant.models import MerchantImage
from buyer.models import Buyer
from common_function.django_redis_cache import Redis
from common_function.get_buyer_id import get_buyer_id
from common_function.get_timestamp import get_after_n_minutes_timestamp

cache = Redis('default')


class ShoppingCartViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)

    def create(self, request):
        # 商品id colorItem_index 个数
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        id = request.data.get('id')
        item_index = request.data.get('item_index')
        item_data = request.data.get('item_data')
        cache_key = 'user:cart:{}'.format(buyer_id)
        if cache.hexists(cache_key, '{}:{}'.format(id, item_index)):
            data = json.loads(cache.hget(cache_key, '{}:{}'.format(id, item_index)))
            item_data['num'] += data['num']
            cache.hset(cache_key, '{}:{}'.format(id, item_index), json.dumps(item_data))
        else:
            cache.hset(cache_key, '{}:{}'.format(id, item_index), json.dumps(item_data))

        result = {
            'code': 1,
            'data': None,
            'message': '购物车数据新增成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def list(self, request):
        # 商品id 商品封面 标题 colorItem colorItem_index 单价 个数 商家店铺名
        type = request.GET.get('type')
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        cache_key = 'user:cart:{}'.format(buyer_id)
        if type == 'getNum':
            cartNum = cache.hlen(cache_key)
            result = {
                'code': 1,
                'data': cartNum,
                'message': '购物车数据获取成功'
            }
        else:
            field_list = cache.hkeys(cache_key)
            data_list = list()
            for field in field_list:
                data = json.loads(cache.hget(cache_key, field))
                data_list.append(data)

            result = {
                'code': 1,
                'data': data_list,
                'message': '购物车数据获取成功'
            }

        return Response(result, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        # 商品id colorItem_index 个数
        original_item_index = request.data.get('original_item_index')
        item_index = request.data.get('item_index')
        num = request.data.get('num')
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        cache_key = 'user:cart:{}'.format(buyer_id)
        # 类型不变则直接修改
        if original_item_index == item_index:
            data = json.loads(cache.hget(cache_key, '{}:{}'.format(pk, item_index)))
            data['num'] = int(num)
            cache.hset(cache_key, '{}:{}'.format(pk, item_index), json.dumps(data))
        else:
            # 若key值修改后存在，则合并num
            if cache.hexists(cache_key, '{}:{}'.format(pk, item_index)):
                original_data = json.loads(cache.hget(cache_key, '{}:{}'.format(pk, original_item_index)))
                data = json.loads(cache.hget(cache_key, '{}:{}'.format(pk, item_index)))
                data['num'] += original_data['num']
                cache.hset(cache_key, '{}:{}'.format(pk, item_index), json.dumps(data))
            else:
                data = json.loads(cache.hget(cache_key, '{}:{}'.format(pk, original_item_index)))
                data['item_index'] = item_index
                cache.hset(cache_key, '{}:{}'.format(pk, item_index), json.dumps(data))
            cache.hdel(cache_key, '{}:{}'.format(pk, original_item_index))

        result = {
            'code': 1,
            'data': None,
            'message': '购物车数据修改成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        delete_list = request.data.get('delete_list')
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        cache_key = 'user:cart:{}'.format(buyer_id)
        for item in delete_list:
            cache.hdel(cache_key, item)

        result = {
            'code': 1,
            'data': None,
            'message': '购物车数据删除成功'
        }

        return Response(result, status=status.HTTP_200_OK)


class OrderViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)
    cache_key_model = 'user:order:{}'

    def create(self, request):
        expiration = get_after_n_minutes_timestamp(15)
        order_data = {
            'info': request.data.get('info'),
            'price': request.data.get('price'),
            'address': request.data.get('address_id'),
            'expiration': expiration
        }
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        buyer = Buyer.objects.get(pk=buyer_id)
        # 保存订单数据
        order = Order.save_data(order_data, buyer)

        result = {
            'code': 1,
            'data': {
                'order_id': order.id
            },
            'message': '订单生成成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def list(self, request):
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        buyer = Buyer.objects.get(pk=buyer_id)

        canceled_data = Order.get_canceled_data(buyer)
        to_be_paid_data = Order.get_to_be_paid_data(buyer)
        to_be_received_data_list, completed_data_list = SinglePurchaseOrder.get_all_single_data(buyer)

        all_data_list = canceled_data + to_be_paid_data + to_be_received_data_list + completed_data_list
        all_data_list = sorted(all_data_list, key=lambda x:x['create_time'], reverse=True)

        for index, item in enumerate(all_data_list):
            all_data_list[index] = self.serialize_order_data(item)

        result = {
            'code': 1,
            'data': {
                'all_data': all_data_list,
                'canceled_data': canceled_data,
                'to_be_paid_data': to_be_paid_data,
                'to_be_received_data': to_be_received_data_list,
                'completed_data': completed_data_list
            },
            'message': '订单获取成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        order_data = Order.get_single_data(pk)
        order_data = self.serialize_order_data(order_data)

        result = {
            'code': 1,
            'data': order_data,
            'message': '订单获取成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    @staticmethod
    def serialize_order_data(order_data):
        info_list = list()
        for item in order_data['info']:
            id, item_index, num = [int(i) for i in item.split(':')]
            commodity = Commodity.get_appoint_commodity(id)
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
                'item_index': item_index,
                'num': num
            }

            # 处理颜色分类数据
            single_data['color_item'] = json.loads(single_data['color_item'])
            for index, color_item in enumerate(single_data['color_item']):
                single_data['color_item'][index]['color'] = SecondColorSelector.get_point_color(color_item['color'][1])
                single_data['color_item'][index]['img'] = MerchantImage.get_image_img(color_item['img'])

            info_list.append(single_data)

        order_data['info'] = info_list

        return order_data


class SinglePurchaseOrderViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)

    def create(self, request):
        order_data = request.data.get('order_data')
        SinglePurchaseOrder.save_data(order_data)

    def list(self, request):
        pass

    def retrieve(self, request, pk):
        pass