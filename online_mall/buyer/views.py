import re

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from django.http import QueryDict
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from .models import Buyer, Address


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

        return Response(result, status=status.HTTP_200_OK)

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
            cache.set('user:defaultAddress:{}'.format(request.data.get('buyer_id')), address_id, settings.APPLET_REFRESH_SECONDS)

        result = {
            'code': 1,
            'data': None,
            'message': '新增地址数据成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def list(self, request):
        buyer_id = request.GET.get('buyer_id')
        buyer = Buyer.objects.get(id=buyer_id)
        address_list = Address.get_data(buyer)

        result = {
            'code': 1,
            'address_list': address_list,
            'message': '获取地址数据成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        buyer_id = self.get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        default_id = cache.get('user:defaultAddress:{}'.format(buyer_id))
        if default_id == int(pk):
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
        print(pk)
        data = QueryDict(request.body)
        print(data)

        result = {
            'code': 1,
            'message': '修改地址数据成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        Address.delete_data(pk)

        buyer_id = self.get_buyer_id(request.environ.get('HTTP_AUTHORIZATION'))
        default_id = cache.get('user:defaultAddress:{}'.format(buyer_id))
        if default_id == int(pk):
            cache.delete('user:defaultAddress:{}'.format(buyer_id))

        result = {
            'code': 1,
            'message': '删除地址数据成功'
        }

        return Response(result, status=status.HTTP_200_OK)

    @staticmethod
    def get_buyer_id(token):
        token = re.search(settings.REGEX_TOKEN, token).group(1)
        token_info = jwt_decode_handler(token)
        user_id = token_info['user_id']
        buyer_id = User.objects.get(pk=user_id).buyer.id

        return buyer_id
