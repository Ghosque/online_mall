from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Buyer


class BuyerViewset(viewsets.ViewSet):

    def create(self, request):
        type = request.GET.get('type')

        if type == 'auth':
            result = self.handle_auth(request)

        elif type == 'login':
            result = self.handle_login(request)

        else:
            result = {
                'code': 0,
                'data': None,
                'message': '类型错误'
            }

        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def handle_auth(cls, request):
        user_data = {
            'open_id': request.data.get('openId'),
            'nickname': request.data.get('nickName'),
            'gender': request.data.get('gender'),
            'avatar': request.data.get('avatarUrl'),
            'language': request.data.get('language'),
            'area': ','.join([request.data.get('country'), request.data.get('province'), request.data.get('city')])
        }
        res = Buyer.create_or_update_user(user_data)
        if res:
            result = {
                'code': res,
                'data': None,
                'message': '新增数据成功'
            }

            return result

        else:
            result = {
                'code': res,
                'data': None,
                'message': '新增数据失败'
            }

            return result

    @classmethod
    def handle_login(cls, request):
        pass
