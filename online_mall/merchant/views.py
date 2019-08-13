from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action

from .models import Merchant
from .serializers import MerchantSerializer


class MerchantsList(viewsets.ViewSet):

    def list(self, request):
        """
        获取所有商家数据
        """
        merchants = Merchant.objects.all()
        serializer = MerchantSerializer(merchants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        新增数据
        """
        serializer = MerchantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=False)
    def check(self, request):
        """
        登录，校验数据
        """
        data = request.data
        serializer = MerchantSerializer(data)
        if serializer.is_valid():
            return Response({'code': 1, 'msg': '登录成功'}, status=status.HTTP_200_OK)
        else:
            return Response({'code': 0, 'msg': '密码错误'}, status=status.HTTP_403_FORBIDDEN)
