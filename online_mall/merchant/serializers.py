from rest_framework import serializers
from .models import Merchant, Shop


class MerchantSerializer(serializers.ModelSerializer):
    """商家数据序列化器"""

    class Meta:
        model = Merchant
        fields = ("id", "merchant_id", "password", "name", "gender", "age", "phone", "id_card", "create_time", "update_time")
        read_only_fields = ("id",)


class ShopSerializer(serializers.ModelSerializer):
    """商店数据序列化器"""
    merchant = MerchantSerializer()

    class Meta:
        model = Shop
        fields = ("id", "shop_id", "name", "star", "status", "create_time", "update_time", "merchant")
        read_only_fields = ("id",)
