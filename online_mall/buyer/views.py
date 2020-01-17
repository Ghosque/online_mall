from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Buyer


class BuyerViewset(viewsets.ViewSet):

    def create(self, request):
        type = request.GET.get('type')

        if type == 'auth':
            self.handle_auth(request)

        elif type == 'login':
            self.handle_login(request)

        else:
            result = {
                'code': 0,
                'data': None,
                'message': '类型错误'
            }

    @classmethod
    def handle_auth(cls, request):
        user_data = {
            'open_id': request.GET.get('openId'),
            'nickname': request.GET.get('nickName'),
            'gender': request.GET.get('gender'),
            'avatar': request.GET.get('avatarUrl'),
            'language': request.GET.get('language'),
            'area': ','.join([request.GET.get('country'), request.GET.get('province'), request.GET.get('city')])
        }
        res = Buyer.create_or_update_user(user_data)
        if res:
            result = {
                'code': res,
                'data': None,
                'message': '新增数据成功'
            }

            return Response(result, status=status.HTTP_200_OK)

        else:
            result = {
                'code': res,
                'data': None,
                'message': '新增数据失败'
            }

            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def handle_login(cls, request):
        pass
