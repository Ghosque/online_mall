from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from .serializers import BuyerLoginSerializer, BuyerRegSerializer
from .models import Buyer
from common.models import MallUser
from common_function.get_id import GetId


class BuyerViewset(viewsets.ViewSet):

    def create(self, request):
        type = request.GET.get('type')

        if type == 'login':
            self.handle_login(request)

        elif type == 'register':
            self.handle_register(request)

        else:
            pass

    @classmethod
    def handle_login(cls, request):
        serializer = BuyerLoginSerializer(data=request.data)
        if not serializer.is_valid():
            result = {
                'code': 0,
                'data': None,
                'message': str(serializer.errors.get('password')[0])
            }
            return Response(result, status=status.HTTP_200_OK)

        mall_user = MallUser.objects.get(phone=request.data['phone'])
        user = mall_user.user
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        cache.set(user.id, token, settings.REFRESH_SECONDS)

        result = {
            'code': 1,
            'data': {
                'token': token,
                'user_id': user.id
            },
            'message': '登录成功'
        }

        return result

    @classmethod
    def get_buyer_id(cls):
        buyer_id = GetId.getId()
        while User.objects.filter(username=buyer_id):
            buyer_id = GetId.getId()

        return buyer_id

    @classmethod
    def handle_register(cls, request):
        serializer = BuyerRegSerializer(data=request.data)
        if not serializer.is_valid():
            if serializer.errors.get('id_card'):
                message = str(serializer.errors.get('id_card')[0])
            else:
                message = str(serializer.errors.get('code')[0])

            result = {
                'code': 0,
                'data': None,
                'message': message
            }
            return Response(result, status=status.HTTP_200_OK)

        buyer_id = cls.get_buyer_id()

        user = User.objects.create_user(
            username=buyer_id,
            password=request.data['password'],
            is_superuser=0,
            is_staff=1
        )

        mall_user = MallUser.objects.create(
            name=request.data['name'],
            gender=request.data['gender'],
            phone=request.data['phone'],
            id_card=request.data['id_card'],
            is_merchant=1,
            user=user
        )
        Buyer.objects.create(
            buyer_id=buyer_id,
            nickname=request.data['nickname'],
            mall_user=mall_user,
        )

        result = {
            'code': 1,
            'data': None,
            'message': '注册成功'
        }

        return result

    @permission_classes([IsAuthenticated])
    def retrieve(self, request, pk):
        pass
