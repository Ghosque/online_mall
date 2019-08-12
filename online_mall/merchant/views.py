from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Merchant
from .serializers import MerchantSerializer, MerchantDetailSerializer


class MerchantsList(APIView):

    def get(self, request):
        """
        获取所有商家数据
        """
        merchants = Merchant.objects.all()
        serializer = MerchantSerializer(merchants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        新增数据
        """
        serializer = MerchantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class MerchantDetail(APIView):

    def get(self, request):
        """
        获取当前商家数据
        """
        merchant_id = request.session.get('merchant', None)
        if not merchant_id:
            return Response({"error": "暂未登录"}, status=status.HTTP_400_BAD_REQUEST)

        merchant = Merchant.objects.get(merchant_id=merchant_id)
        serializer = MerchantSerializer(data=merchant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request):
        """
        登录，校验数据
        """
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        check_result = Merchant.login_check(phone, password)
        if check_result:
            request.session['merchant'] = check_result.merchant_id
            return Response({'code': 1}, status=status.HTTP_200_OK)
        else:
            return Response({'code': 0}, status=status.HTTP_403_FORBIDDEN)
