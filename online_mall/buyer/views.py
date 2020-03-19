from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from .models import Buyer


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
