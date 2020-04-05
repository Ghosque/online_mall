from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from .models import Buyer, Address
from common_function.django_redis_cache import Redis
from common_function.get_buyer_id import get_buyer_id

cache = Redis('default')


class BuyerViewset(viewsets.ViewSet):

    def create(self, request):
        type = request.GET.get('type')

        if type == 'auth':
            result = self.handle_auth(request)

        else:
            result = {
                'code': 0,
                'data': None,
                'message': '类型错误'
            }

        return Response(result, status=status.HTTP_201_CREATED)

    @classmethod
    def handle_auth(cls, request):
        user_data = {
            'open_id': request.data.get('openId'),
            'username': request.data.get('nickName'),
            'gender': request.data.get('gender'),
            'avatar': request.data.get('avatarUrl'),
            'language': request.data.get('language'),
            'area': ','.join([request.data.get('country'), request.data.get('province'), request.data.get('city')])
        }
        res = Buyer.create_or_update_user(user_data)
        if res:
            payload = jwt_payload_handler(res[0])
            token = jwt_encode_handler(payload)
            cache.set('user:token:'+str(res[0].id), token, settings.APPLET_REFRESH_SECONDS)
            result = {
                'code': 1,
                'data': {
                    'buyer_id': res[1].id,
                    'user_id': res[0].id,
                    'token': token
                },
                'message': '新增数据成功'
            }

        else:
            result = {
                'code': 0,
                'data': None,
                'message': '新增数据失败'
            }

        return result


class AddressViewset(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)
    cache_key_model = 'user:defaultAddress:{}'

    def create(self, request):
        buyer = Buyer.objects.get(id=request.data.get('buyer_id'))
        data = {
            'name': request.data.get('name'),
            'phone': request.data.get('phone'),
            'region': request.data.get('region'),
            'detail': request.data.get('detail'),
            'buyer': buyer
        }
        address_id = Address.save_data(data)
        if request.data.get('isDefault'):
            cache.set(self.cache_key_model.format(request.data.get('buyer_id')), address_id, settings.APPLET_REFRESH_SECONDS)

        result = {
            'code': 1,
            'data': None,
            'message': '新增地址数据成功'
        }

        return Response(result, status=status.HTTP_201_CREATED)

    def list(self, request):
        buyer_id = request.GET.get('buyer_id')
        buyer = Buyer.objects.get(id=buyer_id)
        address_list = Address.get_data(buyer)
        default_id = cache.get(self.cache_key_model.format(buyer_id))

        result = {
            'code': 1,
            'address_list': address_list,
            'default_id': default_id,
            'message': '获取地址数据成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        default_id = cache.get(self.cache_key_model.format(buyer_id))
        if default_id == pk:
            isDefault = True
        else:
            isDefault = False

        data = Address.get_single_data(pk)
        data['isDefault'] = isDefault

        result = {
            'code': 1,
            'data': data,
            'message': '获取地址数据成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def update(self, request, pk):
        data = {
            'id': pk,
            'name': request.data['name'],
            'phone': request.data['phone'],
            'region': request.data['region'],
            'detail': request.data['detail']
        }
        code = Address.update_data(data)

        if code:
            buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
            default_id = cache.get(self.cache_key_model.format(buyer_id))
            if default_id == pk and not request.data['isDefault']:
                cache.delete(self.cache_key_model.format(buyer_id))
            elif request.data['isDefault']:
                cache.set(self.cache_key_model.format(buyer_id), int(pk), settings.APPLET_REFRESH_SECONDS)

            msg = '修改地址数据成功'
        else:
            msg = '修改地址数据失败'

        result = {
            'code': code,
            'message': msg
        }

        return Response(result, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        Address.delete_data(pk)

        buyer_id = get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        default_id = cache.get(self.cache_key_model.format(buyer_id))
        if default_id == pk:
            cache.delete(self.cache_key_model.format(buyer_id))

        result = {
            'code': 1,
            'message': '删除地址数据成功'
        }

        return Response(result, status=status.HTTP_200_OK)
