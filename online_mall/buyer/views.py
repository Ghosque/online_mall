import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Buyer, FollowCommodity, FollowShop, CommodityView, CardTicket
from merchant.models import Commodity, MerchantImage
from common.models import SecondColorSelector


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


class CommodityViewset(viewsets.ViewSet):

    def list(self, request):
        type = request.GET.get('type')
        name = None

        if type == 'hot':
            commodity_list = Commodity.get_hot_commodity()
        else:
            commodity_list, name = Commodity.get_appoint_category_commodity(request.GET.get('category_id'))

        for commodity in commodity_list:
            # 处理照片墙数据
            for index, image_id in enumerate(commodity['display_images']):
                commodity['display_images'][index] = MerchantImage.get_image_img(image_id)
            # 处理颜色分类数据
            commodity['color_item'] = json.loads(commodity['color_item'])
            for index, color_item in enumerate(commodity['color_item']):
                commodity['color_item'][index]['color'] = SecondColorSelector.get_point_color(color_item['color'][1])
                commodity['color_item'][index]['img'] = MerchantImage.get_image_img(color_item['img'])
            # 处理属性数据
            commodity['attribute_item'] = json.loads(commodity['attribute_item'])
            for index, attribute_item in enumerate(commodity['attribute_item']):
                commodity['attribute_item'][index] = {attribute_item['attribute']: attribute_item['content']}

        result = {
            'code': 1,
            'data': commodity_list,
            'name': name,
            'message': '获取commodity成功'
        }

        return Response(result, status=status.HTTP_200_OK)


class NoteViewset(viewsets.ViewSet):

    def list(self, request):
        type = request.GET.get('type')
        id = request.GET.get('id')

        buyer = Buyer.objects.get(id=id)

        commodity_follow = FollowCommodity.get_follow(buyer, type)
        shop_follow = FollowShop.get_follow(buyer, type)
        commodity_view = CommodityView.get_user_view(buyer, type)
        card = CardTicket.get_card(buyer, type)

        data = [commodity_follow, shop_follow, commodity_view, card]

        result = {
            'code': 1,
            'data': data,
            'message': '获取note成功'
        }

        return Response(result, status=status.HTTP_200_OK)
