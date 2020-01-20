from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Buyer, FollowCommodity, FollowShop, CommodityView, CardTicket


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

        return Response(result, status=status.HTTP_200_OK)

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
                'code': 1,
                'data': res,
                'message': '新增数据成功'
            }

            return result

        else:
            result = {
                'code': 0,
                'data': None,
                'message': '新增数据失败'
            }

            return result

    @classmethod
    def handle_login(cls, request):
        pass


class NoteViewset(viewsets.ViewSet):

    def list(self, request):
        type = request.GET.get('type')
        id = request.GET.get('id')

        buyer = Buyer.objects.get(id=id)

        commodity_follow_list = FollowCommodity.get_follow(buyer)
        shop_follow_list = FollowShop.get_follow(buyer)
        commodity_view_list = CommodityView.get_user_view(buyer)
        card_list = CardTicket.get_card(buyer)

        if type == 'num':
            data = [len(commodity_follow_list), len(shop_follow_list), len(commodity_view_list), len(card_list)]
        else:
            data = [commodity_follow_list, shop_follow_list, commodity_view_list, card_list]

        result = {
            'code': 1,
            'data': data,
            'message': '新增数据成功'
        }

        return Response(result, status=status.HTTP_200_OK)
