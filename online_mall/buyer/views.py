from rest_framework import status
from django.http import JsonResponse
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
            'open_id': request.data.get('openId'),
            'nickname': request.data.get('nickName'),
            'gender': request.data.get('gender'),
            'avatar': request.data.get('avatarUrl'),
            'language': request.data.get('language'),
            'area': ','.join([request.data.get('country'), request.data.get('province'), request.data.get('city')])
        }
        res = Buyer.create_or_update_user(user_data)
        print(res)
        if res:
            result = {
                'code': res,
                'data': None,
                'message': '新增数据成功'
            }

            return JsonResponse(result)

        else:
            result = {
                'code': res,
                'data': None,
                'message': '新增数据失败'
            }

            return JsonResponse(result)

    @classmethod
    def handle_login(cls, request):
        pass
